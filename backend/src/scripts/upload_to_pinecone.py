"""
Upload all processed documents to Pinecone vector database.

This script runs the complete ingestion pipeline, prepares documents for vectorization,
and uploads them to Pinecone with embeddings. Includes progress tracking, error handling,
and retry logic for robust operation.

Usage:
    python src/scripts/upload_to_pinecone.py
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.ingestion.pipeline import IngestionPipeline
from src.rag.vector_store import PineconeVectorStore


def main():
    """
    Main execution flow for uploading documents to Pinecone.
    
    Orchestrates the complete workflow:
    1. Process all data sources through ingestion pipeline
    2. Prepare documents for vector database
    3. Initialize Pinecone vector store
    4. Upload documents with progress tracking
    5. Display final statistics and test queries
    """
    print("=" * 80)
    print("PINECONE DOCUMENT UPLOAD")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    start_time = time.time()
    
    # Step 1: Initialize and run ingestion pipeline
    print("[1/5] Running ingestion pipeline...")
    print("-" * 80)
    try:
        pipeline = IngestionPipeline()
        results = pipeline.process_all_sources()
        
        print(f"✓ Processed {results['summary']['total']} data sources")
        print(f"  Successful: {results['summary']['successful']}")
        print(f"  Failed: {results['summary']['failed']}")
        print(f"  Quality Score: {results['summary']['quality_score']:.1f}%")
        
        if results['summary']['failed'] > 0:
            print("\n⚠ Warning: Some sources failed to load:")
            for source in results['sources']:
                if source['status'] == 'failed':
                    print(f"  ✗ {source['filepath']}")
                    for error in source['errors']:
                        print(f"    - {error}")
        
    except Exception as e:
        print(f"✗ Error running ingestion pipeline: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 2: Prepare documents for vector database
    print("\n[2/5] Preparing documents for vector database...")
    print("-" * 80)
    try:
        documents = pipeline.prepare_for_vectordb(results)
        print(f"✓ Prepared {len(documents)} documents for upload")
        
        if documents:
            print(f"\nSample document preview:")
            sample = documents[0]
            print(f"  ID: {sample['id']}")
            print(f"  Domain: {sample['metadata'].get('domain', 'N/A')}")
            print(f"  Source Type: {sample['metadata'].get('source_type', 'N/A')}")
            print(f"  Text preview: {sample['text'][:100]}...")
        
    except Exception as e:
        print(f"✗ Error preparing documents: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    if not documents:
        print("\n⚠ No documents to upload. Exiting.")
        return 0
    
    # Step 3: Initialize Pinecone vector store
    print("\n[3/5] Initializing Pinecone vector store...")
    print("-" * 80)
    try:
        store = PineconeVectorStore()
        print("✓ Connected to Pinecone")
        
        # Get initial stats
        initial_stats = store.get_index_stats()
        print(f"  Current vectors in index: {initial_stats['total_vector_count']}")
        print(f"  Index dimension: {initial_stats['dimension']}")
        
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        print("  Please ensure PINECONE_API_KEY, OPENAI_API_KEY, and PINECONE_INDEX_NAME are set in .env")
        return 1
    except Exception as e:
        print(f"✗ Error initializing vector store: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 4: Upload documents to Pinecone
    print(f"\n[4/5] Uploading {len(documents)} documents to Pinecone...")
    print("-" * 80)
    print("This may take several minutes due to API rate limits...")
    print()
    
    upload_start = time.time()
    
    try:
        upload_result = store.upsert_documents(documents, batch_size=50)
        
        upload_time = time.time() - upload_start
        
        print(f"\n✓ Upload complete!")
        print(f"  Total documents: {upload_result['total_documents']}")
        print(f"  Successful: {upload_result['successful_upserts']}")
        print(f"  Failed: {upload_result['failed_upserts']}")
        print(f"  Upload time: {upload_time:.1f} seconds")
        
        if upload_result['failed_upserts'] > 0:
            print(f"\n⚠ Warning: {upload_result['failed_upserts']} documents failed to upload")
        
    except Exception as e:
        print(f"✗ Error uploading documents: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 5: Final statistics and test query
    print("\n[5/5] Final statistics and verification...")
    print("-" * 80)
    
    try:
        # Get final index stats
        final_stats = store.get_index_stats()
        print(f"✓ Index statistics:")
        print(f"  Total vectors: {final_stats['total_vector_count']}")
        print(f"  Dimension: {final_stats['dimension']}")
        if final_stats['namespaces']:
            print(f"  Namespaces: {final_stats['namespaces']}")
        
        # Test query
        print(f"\n✓ Testing query: 'Find Gold PPO plans'...")
        test_results = store.query("Find Gold PPO plans", top_k=3)
        
        if test_results:
            print(f"  Found {len(test_results)} results:")
            for i, result in enumerate(test_results, 1):
                print(f"    {i}. {result['id']} (score: {result['score']:.4f})")
                print(f"       Domain: {result['metadata'].get('domain', 'N/A')}")
        else:
            print("  No results found (this may be normal if index is still updating)")
        
    except Exception as e:
        print(f"⚠ Warning: Could not verify upload: {e}")
        # Don't fail the script if verification fails
    
    # Final summary
    total_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("UPLOAD COMPLETE")
    print("=" * 80)
    print(f"Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    print(f"Documents uploaded: {upload_result['successful_upserts']}")
    print(f"Final vector count: {final_stats['total_vector_count']}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠ Upload interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
