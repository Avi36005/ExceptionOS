from __future__ import annotations

from functools import lru_cache
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # LLM providers
    GROQ_API_KEY: str = ""
    GROQ_API_KEY_2: str = ""
    GROQ_API_KEY_PRIMARY: str = ""
    GROQ_API_KEY_SECONDARY: str = ""
    GROQ_API_KEY_TERTIARY: str = ""
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Groq model to use
    GROQ_MODEL: str = "llama3-70b-8192"
    GROQ_PRIMARY_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_FAST_MODEL: str = "llama-3.1-8b-instant"
    GEMINI_MODEL: str = "gemini-1.5-pro"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Hindsight
    HINDSIGHT_API_KEY: str = ""
    HINDSIGHT_BASE_URL: str = "https://api.hindsight.vectorize.io"
    # Namespace segment in the Hindsight Cloud REST path (/v1/<namespace>/banks/...)
    HINDSIGHT_NAMESPACE: str = "default"

    # ElevenLabs
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"

    # Feature flags
    ENABLE_OPENCLAW: bool = False
    ENABLE_MULTI_PROVIDER_DEBATE: bool = False
    DEMO_MODE: bool = False

    # OpenClaw (optional bonus integration — see app/api/v1/routes/integrations/openclaw.py)
    OPENCLAW_WEBHOOK_SECRET: str = ""

    # GCP / deployment
    GCP_REGION: str = "asia-south1"
    APP_ENV: str = "development"

    # Synthetic data seed
    EXCEPTIONOS_SYNTHETIC_SEED: int = 2026

    # CORS
    CORS_ORIGINS: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.GROQ_API_KEY_PRIMARY and not settings.GROQ_API_KEY:
        settings.GROQ_API_KEY = settings.GROQ_API_KEY_PRIMARY
    if settings.GROQ_API_KEY_SECONDARY and not settings.GROQ_API_KEY_2:
        settings.GROQ_API_KEY_2 = settings.GROQ_API_KEY_SECONDARY
    if settings.GROQ_PRIMARY_MODEL and settings.GROQ_MODEL == "llama3-70b-8192":
        settings.GROQ_MODEL = settings.GROQ_PRIMARY_MODEL
    return settings
