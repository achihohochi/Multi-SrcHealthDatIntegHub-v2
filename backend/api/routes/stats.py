import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from api.dependencies import get_vector_store
from src.rag.vector_store import PineconeVectorStore

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/stats")
def get_index_stats(
    vector_store: PineconeVectorStore = Depends(get_vector_store),
):
    """Get Pinecone index statistics."""
    try:
        raw_stats = vector_store.index.describe_index_stats()
        namespaces = {}
        if raw_stats.namespaces:
            for ns_name, ns_summary in raw_stats.namespaces.items():
                namespaces[ns_name] = {"vector_count": ns_summary.vector_count}
        return JSONResponse(content={
            "total_vector_count": raw_stats.total_vector_count,
            "dimension": raw_stats.dimension,
            "namespaces": namespaces,
        })
    except Exception:
        logger.exception("Failed to fetch index stats")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve index statistics.",
        )
