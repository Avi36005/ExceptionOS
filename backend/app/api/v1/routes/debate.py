"""Multi-agent debate endpoints (separate from exceptions routes for clarity)."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from supabase import Client

from app.agents.orchestrator import Orchestrator
from app.dependencies import get_current_user, get_supabase
from app.llm.provider_router import get_provider_router
from app.memory.hindsight_client import get_hindsight_client
from app.schemas import DataResponse

router = APIRouter(prefix="/debate", tags=["debate"])


def _get_orchestrator(supabase: Client = Depends(get_supabase)) -> Orchestrator:
    return Orchestrator(get_provider_router(), get_hindsight_client(), supabase)


@router.get("/{case_id}/stream")
async def stream_debate(
    case_id: UUID,
    organization_id: UUID = Query(...),
    demo_mode: bool = Query(False),
    current_user: dict = Depends(get_current_user),
    orchestrator: Orchestrator = Depends(_get_orchestrator),
) -> StreamingResponse:
    """SSE stream of the multi-agent debate for a case."""

    async def _gen():
        async for chunk in orchestrator.run_stream(case_id, organization_id, demo_mode=demo_mode):
            yield chunk

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{case_id}/agent-runs")
async def list_agent_runs(
    case_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    resp = (
        supabase.table("agent_runs")
        .select("*")
        .eq("case_id", str(case_id))
        .order("started_at", desc=True)
        .execute()
    )
    return DataResponse(data=resp.data or [])
