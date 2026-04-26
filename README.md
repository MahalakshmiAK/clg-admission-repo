# College Admission Assistant — GenAI

A RAG-powered chatbot for Indian engineering college admissions (IITs, NITs, BITS, VIT).

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Browser  (React 18 + TypeScript, served by Vite)   │
│                                                     │
│  src/api/client.ts  →  fetch /api/v1/chat           │
└────────────────────┬────────────────────────────────┘
                     │  HTTP (Vite proxy in dev,
                     │        direct in production)
┌────────────────────▼────────────────────────────────┐
│  FastAPI  (Python 3.11+)                            │
│                                                     │
│  routers/chat.py      POST /api/v1/chat             │
│  routers/health.py    GET  /api/v1/health           │
│                       GET  /api/v1/health/stats     │
│  core/config.py       pydantic-settings BaseSettings│
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│  RAG Engine  (rag_engine.py)                        │
│                                                     │
│  SentenceTransformers  →  ChromaDB vectorstore      │
│  Balanced multi-college retrieval                    │
│  Groq LLM  (llama-3.3-70b-versatile)                │
└─────────────────────────────────────────────────────┘
```

**Stack summary**

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite 5, CSS Modules |
| Backend | FastAPI, Uvicorn, Pydantic v2, pydantic-settings |
| RAG | LangChain, ChromaDB, SentenceTransformers (all-MiniLM-L6-v2) |
| LLM | Groq API — llama-3.3-70b-versatile |
| Tests | pytest, pytest-asyncio, httpx (ASGI transport) |

- Retrieval now expands the candidate set and balances returned chunks across colleges instead of only favoring a single target institution.

---

## Project structure

```
college-admission-assistance-gen-ai/
├── backend/
│   ├── core/
│   │   └── config.py          # Typed settings (pydantic-settings)
│   ├── routers/
│   │   ├── chat.py            # POST /api/v1/chat
│   │   └── health.py          # GET  /api/v1/health[/stats]
│   ├── data/                  # JSON knowledge base (one or more files)
│   ├── vectorstore/           # ChromaDB files (git-ignored)
│   ├── main.py                # App factory, lifespan, CORS
│   ├── rag_engine.py          # RAG pipeline
│   ├── ingest.py              # One-time vectorstore builder
│   ├── requirements.txt
│   └── .env.example           # ← copy to .env before running
├── frontend/
│   ├── src/
│   │   ├── api/client.ts      # Typed fetch wrapper
│   │   ├── hooks/useChat.ts   # Chat state + loading logic
│   │   ├── types/index.ts     # Shared TypeScript interfaces
│   │   └── components/        # ChatMessage, ChatInput, QuickActions
│   ├── vite.config.ts         # Dev server + /api proxy
│   ├── tsconfig.json
│   └── .env.example           # ← copy to .env.local if needed
├── tests/
│   └── test_api.py            # 11 pytest tests (no live server)
├── pytest.ini
└── .gitignore
```

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- A free [Groq API key](https://console.groq.com)

---

### 1. Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
#python -m pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set GROQ_API_KEY at minimum

# Build the vector database (run once, or after updating data/)
python ingest.py

# Start the API server
python -m uvicorn main:app --reload
#uvicorn main:app --reload
#python -m pip install --user uvicorn
# → API available at http://localhost:8000
# → Docs at http://localhost:8000/docs
```

---

### 2. Frontend

Open a **second terminal**:

```bash
cd frontend

# Install Node dependencies
npm install

# Start the Vite dev server
npm run dev
# → App available at http://localhost:5173
```

The Vite dev server proxies all `/api` requests to `http://localhost:8000`, so no CORS configuration is needed during development.

---

### 3. Running tests

From the **project root**:

```bash
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

Expected output: **11 passed**.

---

### 4. Production build

```bash
cd frontend
npm run build          # outputs to frontend/dist/
npm run typecheck      # runs tsc --noEmit, catches type errors
```

Serve `frontend/dist/` with any static file host (Netlify, Vercel, Nginx).  
Set the `VITE_API_BASE_URL` env variable in your host to point at the deployed backend.

---

## API reference

All routes are versioned under `/api/v1`.

### `POST /api/v1/chat`

Ask a question about college admissions.

**Request body**
```json
{
  "query": "What is the fee structure at IIT Madras?",
  "top_k": 5
}
```

| Field | Type | Constraints | Default |
|---|---|---|---|
| `query` | string | 1–500 chars | required |
| `top_k` | integer | 1–20 | 5 |

**Response**
```json
{
  "answer": "IIT Madras charges approximately ₹1,00,000 per semester...",
  "sources": [
    { "title": "Fee Structure 2024", "college": "IIT Madras", "score": 0.91 }
  ]
}
```

---

### `GET /api/v1/health`

```json
{ "status": "healthy", "engine": "running" }
```

### `GET /api/v1/health/stats`

```json
{
  "status": "healthy",
  "doc_count": 120,
  "embedding_model": "all-MiniLM-L6-v2",
  "llm_model": "llama-3.3-70b-versatile",
  "vector_store_dir": "/path/to/vectorstore"
}
```

---

## Environment variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | Yes | — | Groq API key |
| `ALLOWED_ORIGINS` | No | `http://localhost:5173` | CORS origins (comma-separated) |
| `EMBEDDING_MODEL` | No | `all-MiniLM-L6-v2` | SentenceTransformer model |
| `LLM_MODEL` | No | `llama-3.3-70b-versatile` | Groq model name |
| `LLM_TEMPERATURE` | No | `0.3` | LLM sampling temperature |
| `DEFAULT_TOP_K` | No | `5` | Default RAG chunks to retrieve |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_BASE_URL` | Production only | Deployed backend URL |

---

## Known limitations

- College entity list in `rag_engine.py` is hardcoded — add new colleges to `KNOWN_COLLEGES`.
- No conversation history — each query is independent.
- Ingest must be re-run after updating JSON data files.
