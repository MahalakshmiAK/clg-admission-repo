from langchain_text_splitters import RecursiveCharacterTextSplitter

def get_text_splitter():
    # Create a splitter that breaks text into readable chunks
    try:
        return RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " "],
        )
    except Exception as e:
        # This should rarely fail, but if it does, stop early
        raise RuntimeError(f"Failed to create text splitter: {e}")


def split_text(text: str) -> list[str]:
    # Basic input validation
    if not text or not isinstance(text, str):
        return []

    splitter = get_text_splitter()

    try:
        chunks = splitter.split_text(text)

        # Fallback: if splitting fails or returns empty, return original text
        return chunks if chunks else [text]

    except Exception as e:
        # If something goes wrong during splitting,
        # return the full text as one chunk instead of breaking pipeline
        print(f"Warning: chunking failed, using full text. Error: {e}")
        return [text]