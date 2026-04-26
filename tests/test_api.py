# tests/test_api.py
# Integration tests for the FastAPI backend.
# Run from the project root: pytest tests/ -v
#
# These tests use httpx.AsyncClient with FastAPI's ASGI transport so no
# live server is needed — no network calls, fast execution.

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch

# ── Patch the RAG engine before importing the app ─────────────────────────────
# We mock CollegeAdmissionRAG so tests never need a vectorstore or API key.

MOCK_ANSWER = {
    "answer": "IIT Madras charges approximately ₹1,00,000 per semester.",
    "sources": [
        {"title": "Fee Structure 2024", "college": "IIT Madras", "score": 0.91}
    ],
}

@pytest.fixture(autouse=True)
def mock_rag(monkeypatch):
    """Replace the real RAG system with a lightweight mock for every test."""
    mock_instance = MagicMock()
    mock_instance.answer.return_value = MOCK_ANSWER
    mock_instance.vector_store._collection.count.return_value = 120

    monkeypatch.setattr(
        "main.CollegeAdmissionRAG",
        MagicMock(return_value=mock_instance),
    )
    return mock_instance


@pytest_asyncio.fixture
async def client():
    """Async HTTP client wired directly to the FastAPI app (no live server)."""
    # Import app here so the monkeypatch above is already in place
    from main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ── Health endpoints ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_returns_200(client):
    """GET /api/v1/health must return 200 with correct shape."""
    res = await client.get("/api/v1/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "healthy"
    assert body["engine"] == "running"


@pytest.mark.asyncio
async def test_stats_returns_doc_count(client):
    """GET /api/v1/health/stats must return vectorstore metadata."""
    res = await client.get("/api/v1/health/stats")
    assert res.status_code == 200
    body = res.json()
    assert "doc_count" in body
    assert "embedding_model" in body
    assert "llm_model" in body


# ── Chat endpoint ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_chat_valid_query_returns_answer(client):
    """POST /api/v1/chat with a valid query must return answer + sources."""
    res = await client.post(
        "/api/v1/chat",
        json={"query": "What is the fee structure at IIT Madras?", "top_k": 3},
    )
    assert res.status_code == 200
    body = res.json()
    assert "answer" in body
    assert isinstance(body["answer"], str)
    assert len(body["answer"]) > 0
    assert "sources" in body
    assert isinstance(body["sources"], list)


@pytest.mark.asyncio
async def test_chat_empty_query_returns_422(client):
    """POST /api/v1/chat with an empty string must be rejected by Pydantic (422)."""
    res = await client.post("/api/v1/chat", json={"query": ""})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_chat_whitespace_only_query_returns_422(client):
    """Whitespace-only query is caught by min_length=1 constraint."""
    res = await client.post("/api/v1/chat", json={"query": "   "})
    # Pydantic strips and rejects — expect validation error
    assert res.status_code in (400, 422)


@pytest.mark.asyncio
async def test_chat_query_too_long_returns_422(client):
    """Queries longer than 500 chars must be rejected."""
    long_query = "a" * 501
    res = await client.post("/api/v1/chat", json={"query": long_query})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_chat_top_k_out_of_range_returns_422(client):
    """top_k must be between 1 and 20 — 0 and 21 should both fail."""
    for bad_k in (0, 21):
        res = await client.post(
            "/api/v1/chat", json={"query": "test", "top_k": bad_k}
        )
        assert res.status_code == 422, f"Expected 422 for top_k={bad_k}"


@pytest.mark.asyncio
async def test_chat_default_top_k_is_5(client, mock_rag):
    """When top_k is omitted the RAG engine must be called with k=5."""
    await client.post("/api/v1/chat", json={"query": "Any question"})
    mock_rag.answer.assert_called_once()
    _, kwargs = mock_rag.answer.call_args
    assert kwargs.get("k", None) == 5 or mock_rag.answer.call_args[0][1] == 5


@pytest.mark.asyncio
async def test_chat_sources_have_correct_shape(client):
    """Each source in the response must contain title, college, and score."""
    res = await client.post(
        "/api/v1/chat", json={"query": "BITS Pilani admission"}
    )
    assert res.status_code == 200
    sources = res.json()["sources"]
    for src in sources:
        assert "title" in src
        assert "college" in src
        assert "score" in src
        assert isinstance(src["score"], float)


@pytest.mark.asyncio
async def test_chat_missing_body_returns_422(client):
    """Request with no body at all must be rejected."""
    res = await client.post("/api/v1/chat")
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_rag_error_returns_500(client, mock_rag):
    """If the RAG engine throws, the endpoint must return 500, not crash."""
    mock_rag.answer.side_effect = RuntimeError("Vectorstore unavailable")
    res = await client.post("/api/v1/chat", json={"query": "NIT Trichy fees"})
    assert res.status_code == 500


# ── Route versioning ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_old_unversioned_route_does_not_exist(client):
    """The old /api/chat route must no longer exist — forces v1 adoption."""
    res = await client.post("/api/chat", json={"query": "test"})
    assert res.status_code == 404
