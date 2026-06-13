"""ElevenLabs voice synthesis endpoints."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
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


class VoiceSessionCreate(BaseModel):
    voice_id: str | None = None
    case_id: UUID | None = None
    consent_given: bool = False
    transcript: list[dict] = []
    extracted_fields: dict = {}


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


@router.get("/sessions")
async def list_voice_sessions(
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """List recent ElevenLabs voice sessions for an organisation."""
    resp = (
        supabase.table("voice_sessions")
        .select("*")
        .eq("organization_id", str(organization_id))
        .order("started_at", desc=True)
        .limit(50)
        .execute()
    )
    sessions = []
    for row in resp.data or []:
        sessions.append({
            "id": row.get("id"),
            "organization_id": row.get("organization_id"),
            "status": "failed" if row.get("status") == "error" else row.get("status"),
            "transcript": row.get("transcript_json") or [],
            "extracted_fields": row.get("metadata_json") or {},
            "linked_case_id": row.get("case_id"),
            "created_at": row.get("started_at"),
            "updated_at": row.get("ended_at") or row.get("started_at"),
            **row,
        })
    return DataResponse(data=sessions)


@router.get("/sessions/{session_id}")
async def get_voice_session(
    session_id: UUID,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Return a single voice session transcript and linked case fields."""
    resp = (
        supabase.table("voice_sessions")
        .select("*")
        .eq("id", str(session_id))
        .eq("organization_id", str(organization_id))
        .maybe_single()
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voice session not found")
    row = resp.data
    return DataResponse(data={
        "id": row.get("id"),
        "organization_id": row.get("organization_id"),
        "status": "failed" if row.get("status") == "error" else row.get("status"),
        "transcript": row.get("transcript_json") or [],
        "extracted_fields": row.get("metadata_json") or {},
        "linked_case_id": row.get("case_id"),
        "created_at": row.get("started_at"),
        "updated_at": row.get("ended_at") or row.get("started_at"),
        **row,
    })


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_voice_session(
    payload: VoiceSessionCreate,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Create a tracked voice-assistant session shell."""
    session_id = str(uuid4())
    now = datetime.utcnow().isoformat()
    row = {
        "id": session_id,
        "organization_id": str(organization_id),
        "user_id": current_user.get("sub"),
        "case_id": str(payload.case_id) if payload.case_id else None,
        "agent_id": payload.voice_id,
        "status": "active",
        "consent_given": payload.consent_given,
        "transcript_json": payload.transcript,
        "started_at": now,
    }
    resp = supabase.table("voice_sessions").insert(row).execute()
    created = (resp.data or [row])[0]
    return DataResponse(data={
        "id": created.get("id", session_id),
        "organization_id": created.get("organization_id", str(organization_id)),
        "status": created.get("status", "active"),
        "transcript": created.get("transcript_json") or [],
        "extracted_fields": payload.extracted_fields,
        "linked_case_id": created.get("case_id"),
        "created_at": created.get("started_at", now),
        "updated_at": created.get("started_at", now),
        **created,
    })
