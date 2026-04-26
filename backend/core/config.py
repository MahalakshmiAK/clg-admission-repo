from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Groq API key (empty means LLM won't work)
    groq_api_key: str = ""

    # Allowed frontend URLs (comma-separated string)
    allowed_origins: str = "http://localhost:5173"

    # Path where vector DB is stored
    vector_store_dir: Path = (
        Path(__file__).resolve().parents[1] / "vectorstore"
    )

    # Model configs
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.3

    # API limits
    default_top_k: int = 5
    max_top_k: int = 20
    max_query_length: int = 500

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_allowed_origins(self) -> list[str]:
        # Convert comma-separated string → list
        origins = [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]

        # Fallback to default if empty
        return origins if origins else ["http://localhost:5173"]

    def validate_paths(self):
        # Ensure vectorstore directory exists
        try:
            self.vector_store_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RuntimeError(
                f"Failed to create/access vector store directory: {e}"
            )

    def validate_limits(self):
        # Basic sanity checks for API limits
        if self.default_top_k <= 0:
            raise ValueError("default_top_k must be > 0")

        if self.max_top_k < self.default_top_k:
            raise ValueError("max_top_k must be >= default_top_k")

        if self.max_query_length <= 0:
            raise ValueError("max_query_length must be > 0")


# Create settings instance
settings = Settings()

# Run validations once at startup
settings.validate_paths()
settings.validate_limits()