"""Exception case CRUD + intake + workflow routes."""
from __future__ import annotations

import asyncio
import json
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import StreamingResponse
from supabase import Client

from app.agents.orchestrator import Orchestrator
from app.dependencies import get_current_user, get_supabase
from app.domain.exceptions.repository import ExceptionCaseRepository
from app.domain.exceptions.service import ExceptionCaseService
from app.llm.provider_router import get_provider_router
from app.memory.hindsight_client import get_hindsight_client
from app.schemas import (
    AnalyzeRequest,
    DataResponse,
    DecisionCreate,
    ExceptionCaseCreate,
    ExceptionCaseUpdate,
    MessageResponse,
    OutcomeCreate,
    PaginationMeta,
)

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/exceptions", tags=["exceptions"])


def _get_service(supabase: Client = Depends(get_supabase)) -> ExceptionCaseService:
    return ExceptionCaseService(ExceptionCaseRepository(supabase))


def _get_orchestrator(supabase: Client = Depends(get_supabase)) -> Orchestrator:
    router_ = get_provider_router()
    hindsight = get_hindsight_client()
    return Orchestrator(router_, hindsight, supabase)


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@router.get("/")
async def list_exceptions(
    organization_id: UUID = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    current_user: dict = Depends(get_current_user),
    service: ExceptionCaseService = Depends(_get_service),
) -> DataResponse:
    cases, total = service.list_cases(organization_id, page, page_size, status_filter)
    pages = (total + page_size - 1) // page_size
    return DataResponse(
        data=cases,
        meta=PaginationMeta(total=total, page=page, page_size=page_size, pages=pages).model_dump(),
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_exception(
    payload: ExceptionCaseCreate,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: ExceptionCaseService = Depends(_get_service),
) -> DataResponse:
    case = service.create_case(organization_id, payload, current_user.get("sub"))
    return DataResponse(data=case)


@router.get("/{case_id}")
async def get_exception(
    case_id: UUID,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: ExceptionCaseService = Depends(_get_service),
) -> DataResponse:
    case = service.get_case(case_id, organization_id)
    return DataResponse(data=case)


@router.patch("/{case_id}")
async def update_exception(
    case_id: UUID,
    payload: ExceptionCaseUpdate,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: ExceptionCaseService = Depends(_get_service),
) -> DataResponse:
    case = service.update_case(case_id, organization_id, payload)
    return DataResponse(data=case)


# ---------------------------------------------------------------------------
# Intake
# ---------------------------------------------------------------------------

@router.post("/{case_id}/intake")
async def run_intake(
    case_id: UUID,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
    service: ExceptionCaseService = Depends(_get_service),
) -> DataResponse:
    """Run the intake agent to extract structured facts from the case."""
    from app.agents.intake_agent import IntakeAgent

    case = service.get_case(case_id, organization_id)
    agent = IntakeAgent(get_provider_router())
    result = await agent.run(
        case_id=case_id,
        title=case.get("title", ""),
        description=case.get("description", ""),
        additional_context=case,
    )

    # Save extracted facts
    facts = result.get("output", {}).get("key_facts", [])
    repo = ExceptionCaseRepository(supabase)
    repo.save_facts(case_id, facts)

    # Update urgency if extracted
    urgency = result.get("output", {}).get("urgency")
    if urgency:
        service.update_case(case_id, organization_id, ExceptionCaseUpdate(urgency=urgency))

    # Log event
    repo.add_event(
        case_id=case_id,
        organization_id=organization_id,
        event_type="intake_completed",
        actor_type="agent",
        actor_id="intake_agent",
        payload={"facts_extracted": len(facts)},
    )

    return DataResponse(data=result)


# ---------------------------------------------------------------------------
# Analysis / Debate
# ---------------------------------------------------------------------------

@router.post("/{case_id}/analyze")
async def trigger_analysis(
    case_id: UUID,
    payload: AnalyzeRequest,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: ExceptionCaseService = Depends(_get_service),
    orchestrator: Orchestrator = Depends(_get_orchestrator),
) -> MessageResponse:
    """Trigger the multi-agent debate (non-streaming). Returns immediately, runs in background."""
    service.get_case(case_id, organization_id)

    async def _run():
        async for _ in orchestrator.run_stream(case_id, organization_id, demo_mode=payload.demo_mode):
            pass

    asyncio.create_task(_run())
    return MessageResponse(
        message="Analysis started",
        data={"case_id": str(case_id), "status": "analyzing"},
    )


@router.get("/{case_id}/debate")
async def stream_debate(
    case_id: UUID,
    organization_id: UUID = Query(...),
    demo_mode: bool = Query(False),
    current_user: dict = Depends(get_current_user),
    service: ExceptionCaseService = Depends(_get_service),
    orchestrator: Orchestrator = Depends(_get_orchestrator),
) -> StreamingResponse:
    """SSE stream of the multi-agent debate."""
    service.get_case(case_id, organization_id)

    async def _event_generator():
        async for chunk in orchestrator.run_stream(case_id, organization_id, demo_mode=demo_mode):
            yield chunk

    return StreamingResponse(
        _event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Recommendation
# ---------------------------------------------------------------------------

@router.get("/{case_id}/recommendation")
async def get_recommendation(
    case_id: UUID,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: ExceptionCaseService = Depends(_get_service),
) -> DataResponse:
    rec = service.get_recommendation(case_id, organization_id)
    return DataResponse(data=rec)


# ---------------------------------------------------------------------------
# Decision
# ---------------------------------------------------------------------------

@router.post("/{case_id}/decision", status_code=status.HTTP_201_CREATED)
async def record_decision(
    case_id: UUID,
    payload: DecisionCreate,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: ExceptionCaseService = Depends(_get_service),
) -> DataResponse:
    decision = service.record_decision(
        case_id, organization_id, payload, current_user["sub"]
    )
    return DataResponse(data=decision)


# ---------------------------------------------------------------------------
# Outcome
# ---------------------------------------------------------------------------

@router.post("/{case_id}/outcome", status_code=status.HTTP_201_CREATED)
async def record_outcome(
    case_id: UUID,
    payload: OutcomeCreate,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: ExceptionCaseService = Depends(_get_service),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    outcome = service.record_outcome(
        case_id, organization_id, payload, current_user["sub"]
    )

    # Trigger outcome learning in background
    async def _learn():
        from app.agents.outcome_learning_agent import OutcomeLearningAgent
        from app.domain.organizations.repository import OrganizationRepository

        org_repo = OrganizationRepository(supabase)
        org = org_repo.get_by_id(organization_id)
        bank_id = org.get("hindsight_bank_id", "") if org else ""

        if bank_id:
            case = service.get_case(case_id, organization_id)
            rec = service.get_recommendation(case_id, organization_id)
            decisions = ExceptionCaseRepository(supabase).get_decisions(case_id)
            agent = OutcomeLearningAgent(get_provider_router(), get_hindsight_client())
            await agent.run(
                case_id=case_id,
                bank_id=bank_id,
                case_facts=case,
                recommendation=rec or {},
                human_decision=decisions[0] if decisions else {},
                actual_outcome=payload.model_dump(),
            )

    asyncio.create_task(_learn())
    return DataResponse(data=outcome)


# ---------------------------------------------------------------------------
# Precedents
# ---------------------------------------------------------------------------

@router.get("/{case_id}/precedents")
async def get_precedents(
    case_id: UUID,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: ExceptionCaseService = Depends(_get_service),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    service.get_case(case_id, organization_id)
    links = ExceptionCaseRepository(supabase).get_precedent_links(case_id)
    return DataResponse(data=links)


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------

@router.get("/{case_id}/memory")
async def get_case_memory(
    case_id: UUID,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: ExceptionCaseService = Depends(_get_service),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Recall Hindsight memories related to this case."""
    case = service.get_case(case_id, organization_id)
    from app.domain.organizations.repository import OrganizationRepository

    org = OrganizationRepository(supabase).get_by_id(organization_id)
    bank_id = org.get("hindsight_bank_id", "") if org else ""
    if not bank_id:
        return DataResponse(data={"memories": [], "message": "No Hindsight bank configured"})

    from app.memory.recall_service import RecallService

    query = f"{case.get('title', '')} {case.get('description', '')}"
    memories = await RecallService(get_hindsight_client()).recall_all(bank_id, query)
    return DataResponse(data={"memories": memories, "bank_id": bank_id})


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

@router.get("/{case_id}/audit")
async def get_audit_trail(
    case_id: UUID,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: ExceptionCaseService = Depends(_get_service),
) -> DataResponse:
    events = service.get_audit_trail(case_id, organization_id)
    return DataResponse(data=events)
