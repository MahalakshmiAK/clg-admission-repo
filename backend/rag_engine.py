import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
VECTOR_STORE_DIR = PROJECT_ROOT / "vectorstore"

# Dataset paths
DATASETS = {
    "college_information": DATA_DIR / "enhanced_college_dataset.json",
}

# ------------------ EMBEDDING MODEL ------------------

class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model: {e}")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        try:
            return self.model.encode(texts, normalize_embeddings=True).tolist()
        except Exception as e:
            raise RuntimeError(f"Embedding documents failed: {e}")

    def embed_query(self, text: str) -> list[float]:
        try:
            return self.model.encode([text], normalize_embeddings=True)[0].tolist()
        except Exception as e:
            raise RuntimeError(f"Embedding query failed: {e}")


def build_embedding_model():
    return SentenceTransformerEmbeddings()


# ------------------ RETRIEVAL LOGIC (FIXED) ------------------

def hybrid_retrieve(vector_store, query, k=5):
    """
    Balanced multi-college retrieval (FIXED VERSION)
    """

    try:
        # Expand search space for better coverage
        results = vector_store.similarity_search_with_score(
            query,
            k=k * 6
        )
    except Exception as e:
        raise RuntimeError(f"Vector search failed: {e}")

    scored_results = []

    # Convert scores
    for doc, distance in results:
        try:
            score = 1 / (1 + distance)
            scored_results.append((doc, score))
        except Exception:
            continue

    # Sort globally
    scored_results.sort(key=lambda x: x[1], reverse=True)

    # Deduplicate
    seen = set()
    unique_results = []

    for doc, score in scored_results:
        key = (doc.page_content[:120], doc.metadata.get("college"))

        if key not in seen:
            seen.add(key)
            unique_results.append((doc, score))

    # Group by college
    grouped = {}

    for doc, score in unique_results:
        college = doc.metadata.get("college", "General")

        if college not in grouped:
            grouped[college] = []

        grouped[college].append((doc, score))

    # Balanced selection
    balanced_results = []

    for college, chunks in grouped.items():
        chunks.sort(key=lambda x: x[1], reverse=True)
        balanced_results.extend(chunks[:2])

    # Final ranking
    balanced_results.sort(key=lambda x: x[1], reverse=True)

    return balanced_results[:k]


# ------------------ LLM GENERATION ------------------

class GroqAnswerGenerator:
    def __init__(self, api_key: str):
        try:
            from langchain_groq import ChatGroq

            self.llm = ChatGroq(
                groq_api_key=api_key,
                model_name="llama-3.3-70b-versatile",
                temperature=0.3,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM: {e}")

    def generate(self, query: str, chunks: list[tuple[Document, float]]) -> str:
        from langchain_core.messages import SystemMessage, HumanMessage

        context = "\n".join(
            [
                f"[{doc.metadata.get('college')}] {doc.page_content}"
                for doc, _ in chunks
            ]
        )

        system_prompt = (
            "You are a college admission assistant.\n\n"
            "You help students compare colleges, fees, placements, courses, and admissions clearly.\n\n"

            "RESPONSE RULES:\n"
            "- Use bullet points\n"
            "- Highlight important numbers in **bold**\n"
            "- Keep answers structured and readable\n\n"

            "CRITICAL COMPARISON RULES:\n"
            "- If multiple colleges are present, compare ALL equally\n"
            "- Do NOT ignore any college in context\n"
            "- Use table format for comparisons\n\n"

            "ACCURACY RULE:\n"
            "- If data is missing, say 'Data not available'\n"
            "- Do NOT assume values\n"
        )

        response = self.llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Context:\n{context}\n\nQuery: {query}")
            ]
        )

        return response.content


# ------------------ MAIN RAG CLASS ------------------

class CollegeAdmissionRAG:
    def __init__(self, groq_api_key: str = None):
        self.vector_store = Chroma(
            persist_directory=str(VECTOR_STORE_DIR),
            embedding_function=build_embedding_model(),
        )

        self.generator = (
            GroqAnswerGenerator(groq_api_key)
            if groq_api_key
            else None
        )

    def answer(self, query: str, k: int = 5):
        try:
            chunks = hybrid_retrieve(self.vector_store, query, k)
        except Exception as e:
            return {
                "answer": f"Retrieval error: {e}",
                "sources": [],
            }

        if self.generator:
            answer = self.generator.generate(query, chunks)
        else:
            answer = "API key not provided."

        sources = [
            {
                "title": doc.metadata.get("title"),
                "college": doc.metadata.get("college"),
                "score": round(score, 2),
            }
            for doc, score in chunks
        ]

        return {
            "answer": answer,
            "sources": sources,
        }