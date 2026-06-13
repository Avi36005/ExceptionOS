"""Exception case CRUD + intake + workflow routes."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, Body, Depends, Query, Request, status
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


@router.get("/{case_id}/replay")
async def get_decision_replay(
    case_id: UUID,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: ExceptionCaseService = Depends(_get_service),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Return a unified decision replay timeline for a case."""
    case = service.get_case(case_id, organization_id)
    repo = ExceptionCaseRepository(supabase)
    events: list[dict] = []

    def add_event(event_type: str, ts: str | None, title: str, summary: str, data: dict | None = None) -> None:
        events.append({
            "id": f"{event_type}-{len(events) + 1}",
            "type": event_type,
            "ts": ts or datetime.utcnow().isoformat(),
            "title": title,
            "summary": summary,
            "data": data or {},
        })

    add_event(
        "request_submitted",
        case.get("created_at"),
        "Request submitted",
        case.get("title") or case.get("description") or "Exception request created.",
        case,
    )

    for audit_event in repo.get_audit_events(case_id):
        add_event(
            audit_event.get("event_type", "audit_event"),
            audit_event.get("created_at"),
            audit_event.get("event_type", "Audit event").replace("_", " ").title(),
            f"{audit_event.get('actor_type', 'system')} recorded {audit_event.get('event_type', 'an event')}.",
            audit_event,
        )

    for link in repo.get_precedent_links(case_id):
        add_event(
            "precedents_retrieved",
            link.get("created_at"),
            "Precedent linked",
            f"Similarity score: {link.get('similarity_score', 'n/a')}",
            link,
        )

    recommendation = repo.get_recommendation(case_id)
    if recommendation:
        add_event(
            "recommendation",
            recommendation.get("created_at"),
            "AI recommendation generated",
            recommendation.get("reasoning") or recommendation.get("recommendation_type", "Recommendation ready."),
            recommendation,
        )

    for decision in repo.get_decisions(case_id):
        add_event(
            "final_decision",
            decision.get("decided_at"),
            "Human decision recorded",
            decision.get("reasoning") or decision.get("decision_type", "Decision recorded."),
            decision,
        )

    outcome = repo.get_outcome(case_id)
    if outcome:
        add_event(
            "outcome",
            outcome.get("created_at") or outcome.get("outcome_date"),
            "Outcome recorded",
            outcome.get("actual_outcome") or outcome.get("notes") or "Outcome captured.",
            outcome,
        )

    events.sort(key=lambda event: event.get("ts") or "")
    return DataResponse(data={"case_id": str(case_id), "events": events})


@router.get("/{case_id}/what-changed")
async def get_recommendation_changes(
    case_id: UUID,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: ExceptionCaseService = Depends(_get_service),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Compare the latest recommendation with the previous version."""
    service.get_case(case_id, organization_id)
    resp = (
        supabase.table("recommendations")
        .select("*")
        .eq("case_id", str(case_id))
        .order("version", desc=True)
        .limit(2)
        .execute()
    )
    recommendations = resp.data or []
    current = recommendations[0] if recommendations else None
    previous = recommendations[1] if len(recommendations) > 1 else None

    facts = ExceptionCaseRepository(supabase).get_facts(case_id)
    changed_fields: list[str] = []
    if previous and current:
        for field in ("recommendation_type", "recommended_amount", "conditions", "risk"):
            if previous.get(field) != current.get(field):
                changed_fields.append(field)

    return DataResponse(data={
        "previous_recommendation": previous,
        "current_recommendation": current,
        "changed_fields": changed_fields,
        "new_facts": facts,
        "changed_confidence": {
            "previous": previous.get("confidence") if previous else None,
            "current": current.get("confidence") if current else None,
        },
        "provider_fallback": current.get("provider_summary", {}) if current else {},
    })


@router.post("/{case_id}/answer-question")
async def answer_missing_information_question(
    case_id: UUID,
    payload: dict = Body(...),
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: ExceptionCaseService = Depends(_get_service),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Persist a requester answer from the missing-information flow."""
    service.get_case(case_id, organization_id)
    field = payload.get("field") or payload.get("question_id") or "additional_context"
    answer = payload.get("answer")
    repo = ExceptionCaseRepository(supabase)
    supabase.table("case_facts").insert({
        "id": str(uuid4()),
        "case_id": str(case_id),
        "key": field,
        "value_json": json.dumps(answer),
        "source": "missing_info_answer",
        "confidence": 1.0,
        "verified": True,
        "created_at": datetime.utcnow().isoformat(),
    }).execute()
    repo.add_event(
        case_id=case_id,
        organization_id=organization_id,
        event_type="missing_information_answered",
        actor_type="user",
        actor_id=current_user.get("sub", "unknown"),
        payload={"field": field, "question_id": payload.get("question_id")},
    )
    facts = repo.get_facts(case_id)
    return DataResponse(data={
        "updated_facts": facts,
        "recommendation_readiness": 0.85,
        "what_changed": {"added_field": field, "answer_recorded": bool(answer)},
        "triggered_recall": False,
    })
