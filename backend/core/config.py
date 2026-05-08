"""PME application settings — OpenRouter + Ollama fallback."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Central configuration for the PME backend."""

    # ── OpenRouter (primary LLM provider) ─────────────────────
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Two models, two jobs:
    # PERSONA_MODEL   → mentor voice, style transfer
    # REASONING_MODEL → Socratic scoring, concept extraction
    PERSONA_MODEL: str = "deepseek/deepseek-v3-0324:free"
    REASONING_MODEL: str = "deepseek/deepseek-r1-0528:free"

    # ── Fallback (local Ollama) ────────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_FALLBACK_MODEL: str = "llama3.2:3b"

    # ── Storage ───────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    UPLOAD_DIR: str = "./data/uploads"
    PERSONA_DIR: str = "./data/personas"
    SESSION_DIR: str = "./data/sessions"
    MASTERY_CERT_DIR: str = "./data/mastery_certs"
    SQLITE_URL: str = "sqlite+aiosqlite:///./data/pme.db"

    # ── Thresholds ────────────────────────────────────────────
    DEVIATION_THRESHOLD: float = 0.65
    IDLE_TRIGGER_SECONDS: int = 300
    MASTERY_SCORE_INCREMENT: float = 0.1
    MASTERY_SCORE_DECREMENT: float = 0.05
    MASTERY_CERT_THRESHOLD: float = 0.8
    MASTERY_CERT_MIN_SESSIONS: int = 3
    MASTERY_CERT_MIN_SUCCESSES: int = 5

    # ── Guardian ──────────────────────────────────────────────
    GUARDIAN_MODEL: str = "distilbert-base-uncased"

    # ── Server ────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
