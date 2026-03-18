"""
ET-Pulse application configuration.

All settings are loaded from environment variables (.env file).
Uses pydantic-settings for type-safe, validated configuration.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the ET-Pulse application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "ET-Pulse"
    app_version: str = "1.0.0"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "info"

    # --- Google AI Studio (Gemini Flash) ---
    gemini_api_key: str = ""
    gemini_model_name: str = "gemini-2.0-flash"

    # --- Groq Cloud (Llama 3) ---
    groq_api_key: str = ""
    groq_model_name: str = "llama-3.3-70b-versatile"

    # --- Google Cloud (Veo API) ---
    google_cloud_project: str = ""
    veo_model_name: str = "veo-2.0-generate-001"

    # --- ChromaDB ---
    chroma_persist_dir: str = "./data/chroma"

    # --- Embedding Model ---
    embedding_model_name: str = "all-MiniLM-L6-v2"

    # --- IndicTrans2 ---
    indictrans2_model_dir: str = "./models/indictrans2"

    # --- RSS Feeds ---
    et_rss_feeds: list[str] = [
        "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",
    ]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton)."""
    return Settings()
