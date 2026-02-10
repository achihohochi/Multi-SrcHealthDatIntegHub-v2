"""
FastAPI backend for Multi-Source Healthcare Knowledge Hub.

Wraps the existing RAG pipeline (query_engine + vector_store) with REST endpoints.
Run with: uvicorn main:app --reload --port 8000
"""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from backend/.env
load_dotenv(Path(__file__).parent / ".env")

# Add backend directory to path so `src.*` imports work
backend_dir = str(Path(__file__).parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from api.middleware import RateLimitMiddleware
from api.routes import health, query, sources, stats

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

# ---------------------------------------------------------------------------
# App – disable Swagger UI in production
# ---------------------------------------------------------------------------
is_dev = os.getenv("ENVIRONMENT", "development") == "development"

app = FastAPI(
    title="Healthcare Knowledge Hub API",
    version="2.0.0",
    description="RAG-powered healthcare data API",
    docs_url="/docs" if is_dev else None,
    redoc_url="/redoc" if is_dev else None,
)

# ---------------------------------------------------------------------------
# Middleware  (added first = innermost; CORS must be outermost)
# ---------------------------------------------------------------------------
# Rate limiting: 20 requests/minute per client IP
app.add_middleware(RateLimitMiddleware, max_requests=20, window_seconds=60)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
app.include_router(query.router, prefix="/api", tags=["Query"])
app.include_router(sources.router, prefix="/api", tags=["Sources"])
app.include_router(stats.router, prefix="/api", tags=["Stats"])
app.include_router(health.router, prefix="/api", tags=["Health"])


@app.get("/")
def root():
    return {
        "message": "Healthcare Knowledge Hub API",
        "docs": "/docs" if is_dev else None,
    }
