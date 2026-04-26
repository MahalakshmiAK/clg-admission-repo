# routers/health.py
# Operational endpoints — health check and vectorstore stats.
# Registered in main.py with prefix="/api/v1".

from fastapi import APIRouter, Request
from core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Health check")
async def health():
    """Returns server status. Use this in Docker health checks."""
    return {"status": "healthy", "engine": "running"}


@router.get("/stats", summary="Vectorstore statistics")
async def stats(request: Request):
    """
    Returns the number of documents in the vectorstore, the embedding model
    name, and the configured LLM. Useful for debugging and monitoring.
    """
    rag = request.app.state.rag
    doc_count = 0

    if rag is not None:
        try:
            doc_count = rag.vector_store._collection.count()
        except Exception:
            doc_count = -1  # vectorstore unreachable

    return {
        "status": "healthy",
        "doc_count": doc_count,
        "embedding_model": settings.embedding_model,
        "llm_model": settings.llm_model,
        "vector_store_dir": str(settings.vector_store_dir),
    }
