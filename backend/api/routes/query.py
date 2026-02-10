import logging
import time

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_query_engine
from api.models.requests import QueryRequest
from api.models.responses import ExampleQueriesResponse, QueryResponse, Source
from src.rag.query_engine import RAGQueryEngine

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query_knowledge_base(
    request: QueryRequest,
    query_engine: RAGQueryEngine = Depends(get_query_engine),
):
    """Query the healthcare knowledge base using RAG."""
    try:
        # Build filter dict from request filters
        filter_dict = {}
        if request.domain_filter:
            filter_dict["domain"] = request.domain_filter
        if request.source_type_filter:
            filter_dict["source_type"] = request.source_type_filter
        if request.classification_filter:
            filter_dict["data_classification"] = request.classification_filter

        start_time = time.time()

        # Use filter_dict if any filters were set
        if filter_dict:
            # Temporarily override the query to pass filters
            retrieved_docs = query_engine.vector_store.query(
                query_text=request.question,
                top_k=request.top_k,
                filter_dict=filter_dict,
            )
            context = query_engine._format_context(retrieved_docs)
            answer = query_engine._generate_answer(
                request.question, context, retrieved_docs
            )
            sources = [
                Source(
                    id=doc["id"],
                    score=doc["score"],
                    domain=doc["metadata"].get("domain", "unknown"),
                    source=doc["metadata"].get("source", "unknown"),
                )
                for doc in retrieved_docs
            ]
            result = {
                "question": request.question,
                "answer": answer,
                "sources": sources,
                "domains_searched": [],
            }
        else:
            raw_result = query_engine.query(request.question, top_k=request.top_k)
            sources = [Source(**s) for s in raw_result["sources"]]
            result = {
                "question": raw_result["question"],
                "answer": raw_result["answer"],
                "sources": sources,
                "domains_searched": raw_result["domains_searched"],
            }

        query_time = time.time() - start_time

        return QueryResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result["sources"],
            domains_searched=result["domains_searched"],
            query_time_seconds=round(query_time, 3),
        )

    except Exception:
        logger.exception("Query failed for question: %s", request.question[:100])
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing your query.",
        )


@router.get("/example-queries", response_model=ExampleQueriesResponse)
def get_example_queries(
    query_engine: RAGQueryEngine = Depends(get_query_engine),
):
    """Get example queries for the knowledge base."""
    return ExampleQueriesResponse(queries=query_engine.get_example_queries())
