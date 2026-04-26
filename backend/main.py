from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from routers import chat, health
from rag_engine import CollegeAdmissionRAG


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when server starts
    print("Starting RAG system...")

    if not settings.groq_api_key:
        print("Warning: GROQ_API_KEY not set. LLM may not work.")

    try:
        # Initialize RAG system
        app.state.rag = CollegeAdmissionRAG(
            groq_api_key=settings.groq_api_key or None
        )
        print("RAG system ready.")

    except Exception as e:
        # Fail fast if RAG cannot start
        print(f"Critical error during startup: {e}")
        raise RuntimeError("Failed to initialize RAG system")

    yield  # App runs here

    # Runs on shutdown
    print("Shutting down...")

    try:
        # Clean up resources (if needed in future)
        app.state.rag = None
    except Exception as e:
        # Don't crash during shutdown
        print(f"Warning during shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title="College Admission API",
    version="1.0.0",
    description="Assistant for engineering college admissions",
    lifespan=lifespan,
)


# Enable CORS
try:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_allowed_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
except Exception as e:
    # CORS misconfiguration should fail early
    raise RuntimeError(f"CORS configuration failed: {e}")


# Register routes
app.include_router(chat.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")