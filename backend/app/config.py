from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # LLM providers
    GROQ_API_KEY: str = ""
    GROQ_API_KEY_2: str = ""
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Groq model to use
    GROQ_MODEL: str = "llama3-70b-8192"
    GEMINI_MODEL: str = "gemini-1.5-pro"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Hindsight
    HINDSIGHT_API_KEY: str = ""
    HINDSIGHT_BASE_URL: str = "https://api.hindsight.vectorize.io"

    # ElevenLabs
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"

    # Feature flags
    ENABLE_OPENCLAW: bool = False
    DEMO_MODE: bool = False

    # GCP / deployment
    GCP_REGION: str = "asia-south1"
    APP_ENV: str = "development"

    # Synthetic data seed
    EXCEPTIONOS_SYNTHETIC_SEED: int = 2026

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
