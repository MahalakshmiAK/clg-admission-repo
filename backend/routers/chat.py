# routers/chat.py
# Handles all /api/v1/chat routes.
# Registered in main.py with prefix="/api/v1".

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

# ── Request / Response schemas ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Validated incoming chat payload."""
    query: str = Field(..., min_length=1, max_length=500, description="User question")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of RAG chunks to retrieve")


class SourceItem(BaseModel):
    """A single retrieved source document reference."""
    title: str | None
    college: str | None
    score: float


class ChatResponse(BaseModel):
    """Structured chat response returned to the frontend."""
    answer: str
    sources: list[SourceItem]


# ── Router ─────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse, summary="Ask the admission assistant")
async def chat(request_body: ChatRequest, request: Request):
    """
    Accepts a natural-language query and returns an LLM-generated answer
    grounded in the college admission vector store.
    """
    # Access the RAG system attached to app.state during lifespan startup
    rag = request.app.state.rag

    if rag is None:
        raise HTTPException(status_code=503, detail="RAG system not initialised.")

    try:
        result = rag.answer(request_body.query, k=request_body.top_k)
        return ChatResponse(**result)
    except Exception as exc:
        # Log the real error server-side; return a generic message to the client
        print(f"[ERROR] chat endpoint: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error.")
