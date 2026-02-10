"""
Vector store operations for Pinecone integration.

This module provides a wrapper around Pinecone and OpenAI APIs for embedding
generation and vector database operations in the health data integration system.
"""

import os
import time
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
from tqdm import tqdm


class PineconeVectorStore:
    """
    Handles vector database operations using Pinecone and OpenAI embeddings.
    
    This class manages the connection to Pinecone, generates embeddings using
    OpenAI's API, and provides methods for upserting documents and querying
    the vector database.
    
    Example:
        >>> store = PineconeVectorStore()
        >>> documents = [
        ...     {"id": "doc1", "text": "Sample text", "metadata": {"domain": "eligibility"}}
        ... ]
        >>> result = store.upsert_documents(documents)
        >>> results = store.query("sample query", top_k=10)
    """
    
    def __init__(self):
        """
        Initialize Pinecone and OpenAI clients.
        
        Loads environment variables and initializes connections to Pinecone
        and OpenAI services. Raises ValueError if required environment variables
        are missing.
        
        Raises:
            ValueError: If PINECONE_API_KEY, OPENAI_API_KEY, or PINECONE_INDEX_NAME
                       are not set in environment variables.
            Exception: If connection to Pinecone index fails.
        """
        load_dotenv()
        
        # Get environment variables
        pinecone_key = os.getenv("PINECONE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME")
        
        # Validate required environment variables
        if not pinecone_key:
            raise ValueError("PINECONE_API_KEY environment variable is not set")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        if not index_name:
            raise ValueError("PINECONE_INDEX_NAME environment variable is not set")
        
        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=pinecone_key)
            
            # Initialize OpenAI client
            self.openai_client = OpenAI(api_key=openai_key)
            
            # Connect to index
            self.index = self.pc.Index(index_name)
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize PineconeVectorStore: {str(e)}") from e
    
    def _generate_embeddings(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using OpenAI's embedding API.
        
        Processes texts in batches to avoid rate limits and includes retry logic
        for handling API errors. Adds delays between batches to respect rate limits.
        
        Args:
            texts: List of text strings to generate embeddings for.
            batch_size: Number of texts to process in each batch (default: 100).
            
        Returns:
            List[List[float]]: List of embedding vectors, each with 1536 dimensions.
            
        Raises:
            RuntimeError: If embedding generation fails after retries.
            
        Example:
            >>> store = PineconeVectorStore()
            >>> texts = ["Sample text 1", "Sample text 2"]
            >>> embeddings = store._generate_embeddings(texts)
            >>> print(len(embeddings[0]))  # Should be 1536
        """
        if not texts:
            return []
        
        all_embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for batch_idx in range(0, len(texts), batch_size):
            batch_texts = texts[batch_idx:batch_idx + batch_size]
            batch_num = (batch_idx // batch_size) + 1
            
            # Retry logic with exponential backoff
            max_retries = 3
            retry_count = 0
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    response = self.openai_client.embeddings.create(
                        model="text-embedding-ada-002",
                        input=batch_texts
                    )
                    
                    # Extract embeddings from response
                    batch_embeddings = [item.embedding for item in response.data]
                    all_embeddings.extend(batch_embeddings)
                    success = True
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise RuntimeError(
                            f"Failed to generate embeddings after {max_retries} retries. "
                            f"Error: {str(e)}"
                        ) from e
                    
                    # Exponential backoff: wait 2^retry_count seconds
                    wait_time = 2 ** retry_count
                    print(f"  Retry {retry_count}/{max_retries} after {wait_time}s...")
                    time.sleep(wait_time)
            
            # Add delay between batches to avoid rate limits (except for last batch)
            if batch_num < total_batches:
                time.sleep(1)
        
        return all_embeddings
    
    def upsert_documents(self, documents: List[Dict], batch_size: int = 100) -> Dict:
        """
        Upsert documents to Pinecone vector database.
        
        Generates embeddings for document texts and upserts them to Pinecone
        in batches. Tracks progress and returns a summary of the operation.
        
        Args:
            documents: List of document dictionaries, each containing:
                - id: Unique identifier for the document
                - text: Text content to embed
                - metadata: Dictionary of metadata to store with the vector
            batch_size: Number of vectors to upsert per batch (default: 100).
            
        Returns:
            Dict: Summary dictionary containing:
                - total_documents: Total number of documents processed
                - successful_upserts: Number of successfully upserted documents
                - failed_upserts: Number of failed upserts
                - time_elapsed_seconds: Total time taken for the operation
                
        Example:
            >>> store = PineconeVectorStore()
            >>> docs = [
            ...     {"id": "doc1", "text": "Sample text", "metadata": {"domain": "eligibility"}}
            ... ]
            >>> result = store.upsert_documents(docs)
            >>> print(f"Upserted {result['successful_upserts']} documents")
        """
        if not documents:
            return {
                "total_documents": 0,
                "successful_upserts": 0,
                "failed_upserts": 0,
                "time_elapsed_seconds": 0.0
            }
        
        start_time = time.time()
        
        # Extract texts for embedding generation
        texts = [doc["text"] for doc in documents]
        
        print(f"Generating embeddings for {len(texts)} documents...")
        embeddings = self._generate_embeddings(texts, batch_size=batch_size)
        
        # Prepare vectors for Pinecone format: (id, embedding, metadata).
        # Store text in metadata so the LLM receives document content at query time.
        # Truncate to 2000 chars to keep Pinecone metadata and storage low.
        vectors = []
        for doc, embedding in zip(documents, embeddings):
            meta = dict(doc.get("metadata") or {})
            meta["text"] = (doc.get("text") or "")[:2000]
            vectors.append((doc["id"], embedding, meta))
        
        # Upsert to Pinecone in batches
        successful_upserts = 0
        failed_upserts = 0
        total_batches = (len(vectors) + batch_size - 1) // batch_size
        
        print(f"Upserting {len(vectors)} vectors in {total_batches} batches...")
        
        for batch_idx in range(0, len(vectors), batch_size):
            batch_vectors = vectors[batch_idx:batch_idx + batch_size]
            batch_num = (batch_idx // batch_size) + 1
            
            try:
                print(f"Upserting batch {batch_num}/{total_batches}...")
                self.index.upsert(vectors=batch_vectors)
                successful_upserts += len(batch_vectors)
                
            except Exception as e:
                print(f"  Error upserting batch {batch_num}: {str(e)}")
                failed_upserts += len(batch_vectors)
        
        end_time = time.time()
        time_elapsed = end_time - start_time
        
        return {
            "total_documents": len(documents),
            "successful_upserts": successful_upserts,
            "failed_upserts": failed_upserts,
            "time_elapsed_seconds": time_elapsed
        }
    
    def query(self, query_text: str, top_k: int = 10, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Query the Pinecone vector database with a text query.
        
        Generates an embedding for the query text and searches for similar
        vectors in the database. Returns results sorted by relevance score.
        
        Args:
            query_text: The text query to search for.
            top_k: Number of top results to return (default: 10).
            filter_dict: Optional metadata filter dictionary for filtering results
                        (e.g., {"domain": "eligibility"}).
                        
        Returns:
            List[Dict]: List of match dictionaries, each containing:
                - id: Document ID
                - score: Similarity score (higher is more similar)
                - metadata: Document metadata dictionary
            Results are sorted by score in descending order.
            
        Example:
            >>> store = PineconeVectorStore()
            >>> results = store.query("Gold PPO plans", top_k=10)
            >>> for result in results:
            ...     print(f"{result['id']}: {result['score']:.3f}")
        """
        if not query_text or not isinstance(query_text, str):
            raise ValueError("query_text must be a non-empty string")
        
        try:
            # Generate embedding for query
            query_embeddings = self._generate_embeddings([query_text], batch_size=1)
            query_embedding = query_embeddings[0]
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Parse results into list of dicts
            matches = []
            for match in results.matches:
                matches.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                })
            
            # Results are already sorted by score (descending) from Pinecone
            return matches
            
        except Exception as e:
            raise RuntimeError(f"Failed to query Pinecone: {str(e)}") from e
    
    def get_index_stats(self) -> Dict:
        """
        Get statistics about the Pinecone index.
        
        Retrieves information about the index including dimension, total
        vector count, and namespace statistics.
        
        Returns:
            Dict: Dictionary containing:
                - dimension: Vector dimension (should be 1536 for text-embedding-ada-002)
                - total_vector_count: Total number of vectors in the index
                - namespaces: Dictionary of namespace statistics if available
                
        Example:
            >>> store = PineconeVectorStore()
            >>> stats = store.get_index_stats()
            >>> print(f"Total vectors: {stats['total_vector_count']}")
        """
        try:
            stats = self.index.describe_index_stats()
            
            return {
                "dimension": stats.dimension,
                "total_vector_count": stats.total_vector_count,
                "namespaces": dict(stats.namespaces) if stats.namespaces else {}
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to get index stats: {str(e)}") from e


def main():
    """
    Test the PineconeVectorStore with sample documents.
    
    Creates sample documents, initializes the vector store, upserts documents,
    performs a test query, and displays results.
    """
    print("=" * 80)
    print("Pinecone Vector Store Test")
    print("=" * 80)
    
    try:
        # Initialize vector store
        print("\n1. Initializing PineconeVectorStore...")
        store = PineconeVectorStore()
        print("✓ Successfully initialized")
        
        # Get initial index stats
        print("\n2. Getting initial index stats...")
        initial_stats = store.get_index_stats()
        print(f"  Dimension: {initial_stats['dimension']}")
        print(f"  Total vectors: {initial_stats['total_vector_count']}")
        print(f"  Namespaces: {initial_stats['namespaces']}")
        
        # Create sample documents
        print("\n3. Creating sample documents...")
        sample_documents = [
            {
                "id": "sample_doc_1",
                "text": "Gold PPO plan offers comprehensive coverage with low copays and no deductible for primary care visits.",
                "metadata": {
                    "domain": "benefits",
                    "source_type": "internal",
                    "plan_type": "Gold PPO",
                    "data_classification": "public"
                }
            },
            {
                "id": "sample_doc_2",
                "text": "Member ID WHP100001 has active status with Gold PPO plan effective since 2024-01-01.",
                "metadata": {
                    "domain": "eligibility",
                    "source_type": "internal",
                    "member_id": "WHP100001",
                    "data_classification": "PII"
                }
            },
            {
                "id": "sample_doc_3",
                "text": "Claim CLM-2025-001234 processed for member WHP100001 with CPT code 99213 for office visit.",
                "metadata": {
                    "domain": "claims",
                    "source_type": "internal",
                    "claim_id": "CLM-2025-001234",
                    "data_classification": "PII"
                }
            }
        ]
        print(f"✓ Created {len(sample_documents)} sample documents")
        
        # Upsert documents
        print("\n4. Upserting documents to Pinecone...")
        upsert_result = store.upsert_documents(sample_documents)
        print(f"✓ Upsert complete:")
        print(f"  Total documents: {upsert_result['total_documents']}")
        print(f"  Successful: {upsert_result['successful_upserts']}")
        print(f"  Failed: {upsert_result['failed_upserts']}")
        print(f"  Time elapsed: {upsert_result['time_elapsed_seconds']:.2f} seconds")
        
        # Wait a moment for index to update
        print("\n5. Waiting for index to update...")
        time.sleep(2)
        
        # Test query
        print("\n6. Testing query: 'Find Gold PPO plans'...")
        query_results = store.query("Find Gold PPO plans", top_k=10)
        print(f"✓ Found {len(query_results)} results:")
        for i, result in enumerate(query_results, 1):
            print(f"\n  Result {i}:")
            print(f"    ID: {result['id']}")
            print(f"    Score: {result['score']:.4f}")
            print(f"    Domain: {result['metadata'].get('domain', 'N/A')}")
            print(f"    Text preview: {result['metadata'].get('text', 'N/A')[:80]}...")
        
        # Get final index stats
        print("\n7. Getting final index stats...")
        final_stats = store.get_index_stats()
        print(f"  Dimension: {final_stats['dimension']}")
        print(f"  Total vectors: {final_stats['total_vector_count']}")
        print(f"  Namespaces: {final_stats['namespaces']}")
        
        print("\n" + "=" * 80)
        print("Test Complete")
        print("=" * 80)
        
    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("Please ensure PINECONE_API_KEY, OPENAI_API_KEY, and PINECONE_INDEX_NAME are set in .env")
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
