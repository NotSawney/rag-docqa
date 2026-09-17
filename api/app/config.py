"""Settings loaded from environment (see .env.example)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    database_url: str = "postgresql://rag:rag@db:5432/rag"

    # Generation provider: "anthropic" (default/production) or "ollama" (local,
    # free, offline — for e2e testing without spending the Claude key).
    llm_provider: str = "anthropic"

    # Browser origins allowed to call the API (comma-separated). The Vite/nginx
    # UI lives on a different origin, so CORS must permit it explicitly.
    cors_origins: str = "http://localhost:5173"

    # Claude generation models (spec: Haiku default, escalate to Sonnet).
    answer_model: str = "claude-haiku-4-5"
    escalation_model: str = "claude-sonnet-5"
    # Questions longer than this (chars) escalate to the stronger model.
    escalation_char_threshold: int = 300

    # Local Ollama (used only when llm_provider == "ollama").
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "qwen3:4b-instruct-2507-q4_K_M"

    # Local embedding model — 384-dim, self-hosted, no per-token cost.
    embed_model: str = "all-MiniLM-L6-v2"
    embed_dim: int = 384

    top_k: int = 5
    # Cosine similarity below this = "not in the documents" (guard refuses).
    score_threshold: float = 0.35

    # Chunking
    chunk_words: int = 180
    chunk_overlap_words: int = 40


settings = Settings()
