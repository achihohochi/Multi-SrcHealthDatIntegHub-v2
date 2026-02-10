"""Simple Pinecone connection test"""
import os
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Test Pinecone
print("Testing Pinecone connection...")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
stats = index.describe_index_stats()
print(f"✓ Pinecone connected: {stats.total_vector_count} vectors")

# Test OpenAI
print("\nTesting OpenAI connection...")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.embeddings.create(model="text-embedding-ada-002", input=["test"])
print(f"✓ OpenAI connected: embedding dimension {len(response.data[0].embedding)}")

print("\n✅ All connections working!")
