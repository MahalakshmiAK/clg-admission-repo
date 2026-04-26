import json
import os
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

from rag_engine import build_embedding_model, DATASETS, VECTOR_STORE_DIR
from utils.chunking import split_text


def load_json_data():
    documents = []

    for category, file_path in DATASETS.items():
        if not file_path.exists():
            print(f"Warning: {file_path} not found, skipping...")
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        if not isinstance(data, list):
            continue

        for item in data:
            try:
                content = (
                    f"Title: {item.get('title', '')}\n"
                    f"Content: {item.get('content', '')}"
                )

                college = item.get("college", "General")
                college = college.strip() if isinstance(college, str) else "General"

                metadata = {
                    "source": item.get("category", category),
                    "college": college,
                    "title": item.get("title", "Untitled"),
                }

                chunks = split_text(content)

                for i, chunk in enumerate(chunks):
                    documents.append(
                        Document(
                            page_content=chunk,
                            metadata={**metadata, "chunk_id": i},
                        )
                    )

            except Exception as e:
                print(f"Skipping bad record: {e}")
                continue

    return documents


def run_ingestion():
    print("Loading datasets...")
    raw_docs = load_json_data()

    if not raw_docs:
        print("No data found.")
        return

    print(f"Encoding {len(raw_docs)} chunks...")

    embedding_model = build_embedding_model()

    Chroma.from_documents(
        documents=raw_docs,
        embedding=embedding_model,
        persist_directory=str(VECTOR_STORE_DIR),
    )

    print("Ingestion complete.")


if __name__ == "__main__":
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    run_ingestion()