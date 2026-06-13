"""Service layer for exception cases."""
from __future__ import annotations

import json
from typing import Any
from uuid import UUID

import structlog
from fastapi import HTTPException, status

from app.domain.exceptions.repository import ExceptionCaseRepository
from app.schemas import (
    DecisionCreate,
    ExceptionCaseCreate,
    ExceptionCaseUpdate,
    OutcomeCreate,
)

logger = structlog.get_logger(__name__)


class ExceptionCaseService:
    def __init__(self, repo: ExceptionCaseRepository):
        self.repo = repo

    def list_cases(
        self,
        organization_id: UUID,
        page: int,
        page_size: int,
        status_filter: str | None,
    ) -> tuple[list[dict], int]:
        return self.repo.list(organization_id, page, page_size, status_filter)

    def get_case(self, case_id: UUID, organization_id: UUID) -> dict:
        case = self.repo.get_by_id(case_id, organization_id)
        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
        return case

    def create_case(
        self,
        organization_id: UUID,
        payload: ExceptionCaseCreate,
        requester_id: str | None,
    ) -> dict:
        data = {k: v for k, v in payload.model_dump().items() if v is not None}
        # Convert UUID fields to str
        for key in ("category_id", "department_id"):
            if data.get(key):
                data[key] = str(data[key])
        return self.repo.create(organization_id, data, requester_id)

    def update_case(self, case_id: UUID, organization_id: UUID, payload: ExceptionCaseUpdate) -> dict:
        self.get_case(case_id, organization_id)
        data = {k: v for k, v in payload.model_dump().items() if v is not None}
        if "assignee_user_id" in data:
            data["assignee_user_id"] = str(data["assignee_user_id"])
        updated = self.repo.update(case_id, organization_id, data)
        if not updated:
            raise HTTPException(status_code=500, detail="Update failed")
        return updated

    def get_recommendation(self, case_id: UUID, organization_id: UUID) -> dict:
        self.get_case(case_id, organization_id)
        rec = self.repo.get_recommendation(case_id)
        if not rec:
            raise HTTPException(status_code=404, detail="No recommendation generated yet")
        # Deserialise JSON columns
        for col in ("conditions_json", "risk_json", "provider_summary_json", "hindsight_evidence_json"):
            if col in rec and rec[col]:
                try:
                    rec[col.replace("_json", "")] = json.loads(rec[col])
                except Exception:
                    pass
        return rec

    def record_decision(
        self,
        case_id: UUID,
        organization_id: UUID,
        payload: DecisionCreate,
        decided_by: str,
    ) -> dict:
        self.get_case(case_id, organization_id)
        rec = self.repo.get_recommendation(case_id)
        data: dict[str, Any] = {
            "decision_type": payload.decision_type.value,
            "reasoning": payload.reasoning,
            "conditions_json": json.dumps(payload.conditions),
            "override": payload.override,
        }
        if payload.approved_amount is not None:
            data["approved_amount"] = payload.approved_amount
        if rec:
            data["recommendation_id"] = rec["id"]

        decision = self.repo.save_decision(case_id, data, decided_by)

        # Update case status
        status_map = {
            "approved": "approved",
            "partially_approved": "partially_approved",
            "denied": "denied",
            "escalated": "escalated",
        }
        new_status = status_map.get(payload.decision_type.value, "pending_decision")
        self.repo.update(case_id, organization_id, {"status": new_status})

        # Audit event
        self.repo.add_event(
            case_id=case_id,
            organization_id=organization_id,
            event_type="decision_recorded",
            actor_type="user",
            actor_id=decided_by,
            payload={"decision_type": payload.decision_type.value},
        )
        return decision

    def record_outcome(
        self,
        case_id: UUID,
        organization_id: UUID,
        payload: OutcomeCreate,
        recorded_by: str,
    ) -> dict:
        self.get_case(case_id, organization_id)
        decisions = self.repo.get_decisions(case_id)
        data: dict[str, Any] = {
            "actual_outcome": payload.actual_outcome,
            "notes": payload.notes,
        }
        if payload.outcome_date:
            data["outcome_date"] = payload.outcome_date.isoformat()
        if payload.financial_impact is not None:
            data["financial_impact"] = payload.financial_impact
        if decisions:
            data["decision_id"] = decisions[0]["id"]

        outcome = self.repo.save_outcome(case_id, data, recorded_by)

        self.repo.update(case_id, organization_id, {"status": "closed"})
        return outcome

    def get_audit_trail(self, case_id: UUID, organization_id: UUID) -> list[dict]:
        self.get_case(case_id, organization_id)
        return self.repo.get_audit_events(case_id)
