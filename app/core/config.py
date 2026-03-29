"""
aether_ai — Core Configuration
Auto-detects LLM: Groq (if GROQ_API_KEY is set) else local Ollama
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    APP_PORT: int = 8000

    # Ollama (local LLM — default, no API key needed)
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_MODEL: str = "llama3.1:8b"

    # Groq (optional cloud LLM — set key to enable)
    GROQ_API_KEY: str = ""

    # Economic Times RSS feeds
    ET_RSS_MARKETS: str = "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"
    ET_RSS_TECH: str = "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms"
    ET_RSS_STARTUP: str = "https://economictimes.indiatimes.com/small-biz/startups/rssfeeds/18949484.cms"
    ET_RSS_ECONOMY: str = "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms"
    ET_RSS_POLICY: str = "https://economictimes.indiatimes.com/news/politics-and-nation/rssfeeds/12988124.cms"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()


def get_llm_client():
    """
    Returns an openai.OpenAI client pointed at:
    - Groq cloud, if GROQ_API_KEY is set in .env
    - Local Ollama, otherwise (default for team repo — no secrets needed)
    """
    import openai
    if settings.GROQ_API_KEY:
        return openai.OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        ), "llama3-8b-8192"
    else:
        return openai.OpenAI(
            api_key="ollama",
            base_url=settings.OLLAMA_BASE_URL,
        ), settings.OLLAMA_MODEL
