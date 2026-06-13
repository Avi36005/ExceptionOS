"""ElevenLabs voice synthesis endpoints."""
from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from supabase import Client

from app.config import get_settings
from app.dependencies import get_current_user, get_supabase
from app.schemas import DataResponse

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/voice", tags=["voice"])


class VoiceRequest(BaseModel):
    text: str
    voice_id: str | None = None
    model_id: str = "eleven_multilingual_v2"


@router.post("/synthesize")
async def synthesize_speech(
    payload: VoiceRequest,
    current_user: dict = Depends(get_current_user),
) -> StreamingResponse:
    """Convert text to speech using ElevenLabs."""
    settings = get_settings()
    if not settings.ELEVENLABS_API_KEY:
        raise HTTPException(status_code=503, detail="ElevenLabs API key not configured")

    import httpx

    voice_id = payload.voice_id or settings.ELEVENLABS_VOICE_ID
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    body = {
        "text": payload.text,
        "model_id": payload.model_id,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }

    async def _stream():
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=body, headers=headers) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_bytes():
                    yield chunk

    return StreamingResponse(
        _stream(),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=speech.mp3"},
    )


@router.get("/voices")
async def list_voices(
    current_user: dict = Depends(get_current_user),
) -> DataResponse:
    """List available ElevenLabs voices."""
    settings = get_settings()
    if not settings.ELEVENLABS_API_KEY:
        raise HTTPException(status_code=503, detail="ElevenLabs API key not configured")

    import httpx

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": settings.ELEVENLABS_API_KEY},
        )
        resp.raise_for_status()
        return DataResponse(data=resp.json())
