import logging
import os

from fastapi import APIRouter

from api.dependencies import get_vector_store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def health_check():
    """Check system health and connectivity."""
    pinecone_ok = False
    openai_ok = False
    vector_count = 0

    try:
        vector_store = get_vector_store()
        stats = vector_store.get_index_stats()
        vector_count = stats["total_vector_count"]
        pinecone_ok = True
    except Exception:
        logger.warning("Pinecone health check failed", exc_info=True)

    try:
        vector_store = get_vector_store()
        # Verify OpenAI client is initialised and API key is present
        openai_ok = (
            hasattr(vector_store, "openai_client")
            and vector_store.openai_client is not None
            and bool(os.getenv("OPENAI_API_KEY"))
        )
    except Exception:
        logger.warning("OpenAI health check failed", exc_info=True)

    status = "ok" if (pinecone_ok and openai_ok) else "degraded"

    return {
        "status": status,
        "pinecone_connected": pinecone_ok,
        "openai_connected": openai_ok,
        "vector_count": vector_count,
    }
