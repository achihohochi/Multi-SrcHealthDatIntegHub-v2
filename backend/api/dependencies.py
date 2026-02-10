import sys
from functools import lru_cache
from pathlib import Path

# Add backend directory to path so src imports work
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from src.rag.vector_store import PineconeVectorStore
from src.rag.query_engine import RAGQueryEngine


@lru_cache()
def get_vector_store() -> PineconeVectorStore:
    return PineconeVectorStore()


@lru_cache()
def get_query_engine() -> RAGQueryEngine:
    vector_store = get_vector_store()
    return RAGQueryEngine(vector_store)
