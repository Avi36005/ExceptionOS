"""Health check endpoint."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from supabase import Client

from app.config import Settings, get_settings
from app.dependencies import get_supabase

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    settings: Settings = Depends(get_settings),
    supabase: Client = Depends(get_supabase),
) -> dict:
    """Return system health status."""
    db_ok = False
    db_error = None
    try:
        supabase.table("organizations").select("id").limit(1).execute()
        db_ok = True
    except Exception as exc:
        db_error = str(exc)

    return {
        "status": "ok" if db_ok else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "services": {
            "database": {"status": "ok" if db_ok else "error", "error": db_error},
            "hindsight": {"status": "configured" if settings.HINDSIGHT_API_KEY else "not_configured"},
            "groq": {"status": "configured" if settings.GROQ_API_KEY else "not_configured"},
            "openclaw": {"status": "enabled" if settings.ENABLE_OPENCLAW else "disabled"},
        },
    }
