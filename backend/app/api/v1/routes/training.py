"""Training scenario endpoints."""
from __future__ import annotations

import json
import random
from datetime import datetime
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.config import get_settings
from app.dependencies import get_current_user, get_supabase
from app.schemas import DataResponse

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/training", tags=["training"])

_SCENARIO_TEMPLATES = [
    {
        "title": "Customer Discount Exception — Long-term Partner",
        "description": "A key account manager requests a 35% discount for a 5-year customer whose contract is up for renewal.",
        "entity_name": "Acme Corp",
        "requested_amount": 50000,
        "urgency": "high",
        "category": "discount",
    },
    {
        "title": "Vendor Payment Terms Extension",
        "description": "Finance team requests 90-day payment terms for a critical supplier instead of standard 30-day terms.",
        "entity_name": "SupplyChain Ltd",
        "requested_amount": 200000,
        "urgency": "medium",
        "category": "payment_terms",
    },
    {
        "title": "SLA Breach Compensation",
        "description": "Customer support requests approval to compensate a client for a 4-hour SLA breach with service credits.",
        "entity_name": "TechStart Inc",
        "requested_amount": 15000,
        "urgency": "critical",
        "category": "compensation",
    },
    {
        "title": "Budget Reallocation for Q4 Campaign",
        "description": "Marketing requests reallocation of $80k from operations budget to support an unexpected partnership opportunity.",
        "entity_name": "Internal",
        "requested_amount": 80000,
        "urgency": "high",
        "category": "budget",
    },
    {
        "title": "Regulatory Compliance Exception",
        "description": "Legal requests a temporary 30-day exception to data retention policy while migration completes.",
        "entity_name": "IT Department",
        "requested_amount": None,
        "urgency": "critical",
        "category": "compliance",
    },
]


@router.get("/scenarios")
async def list_scenarios(
    current_user: dict = Depends(get_current_user),
) -> DataResponse:
    """Return training scenarios with synthetic data."""
    settings = get_settings()
    rng = random.Random(settings.EXCEPTIONOS_SYNTHETIC_SEED)

    scenarios = []
    for i, template in enumerate(_SCENARIO_TEMPLATES):
        scenario = {
            "id": str(uuid4()),
            "scenario_number": i + 1,
            "difficulty": rng.choice(["easy", "medium", "hard"]),
            "expected_outcome": rng.choice(["approve", "deny", "partially_approve", "escalate"]),
            **template,
        }
        scenarios.append(scenario)

    return DataResponse(data=scenarios)


@router.post("/scenarios/{scenario_id}/run")
async def run_training_scenario(
    scenario_id: str,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Create a training case from a scenario and run analysis."""
    # Find scenario
    settings = get_settings()
    rng = random.Random(settings.EXCEPTIONOS_SYNTHETIC_SEED)
    scenarios = _SCENARIO_TEMPLATES
    template = rng.choice(scenarios)

    # Create a real case for training purposes
    case_id = str(uuid4())
    now = datetime.utcnow().isoformat()
    supabase.table("exception_cases").insert({
        "id": case_id,
        "organization_id": str(organization_id),
        "case_number": f"TRN-{case_id[:8].upper()}",
        "title": f"[TRAINING] {template['title']}",
        "description": template["description"],
        "entity_name": template.get("entity_name"),
        "requested_amount": template.get("requested_amount"),
        "urgency": template.get("urgency", "medium"),
        "status": "submitted",
        "version": 1,
        "created_at": now,
        "updated_at": now,
    }).execute()

    return DataResponse(
        data={
            "case_id": case_id,
            "scenario": template,
            "message": "Training case created. Use /exceptions/{case_id}/debate to run analysis.",
        }
    )
