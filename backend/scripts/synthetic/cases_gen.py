"""Deterministic synthetic dataset assembly.

This stage turns the lower-level company/persona/policy helpers into a
loader-friendly JSON payload. It deliberately avoids writing synthetic
personas into FK-backed user columns: fictional users are embedded as JSON
facts/artifacts because `profiles` is tied to Supabase Auth.
"""
from __future__ import annotations

import random
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from typing import Any

from faker import Faker

from scripts.synthetic.config import (
    CASE_STATUS_WEIGHTS,
    DEMO_SMALL_HERO_CASE_RANGE,
    DEMO_SMALL_OTHER_CASE_RANGE,
    EXCEPTION_CATEGORY_DEFS,
    FULL_SYNTHETIC_CASE_RANGE,
    HERO_COMPANY_SLUG,
    MODE_DEMO_SMALL,
    MODE_FULL_SYNTHETIC,
    URGENCY_WEIGHTS,
    CompanyTemplate,
    companies_for_mode,
)
from scripts.synthetic.ids import deterministic_id_str
from scripts.synthetic.personas import Persona, generate_personas, personas_by_role
from scripts.synthetic.policies_gen import PolicyRow, generate_policies_for_company

UTC = timezone.utc

DEPARTMENTS = (
    "Customer Success",
    "Finance",
    "Sales",
    "Engineering",
    "Operations",
    "Legal",
)

CATEGORY_BY_FOCUS = {
    "Late refunds": "late_refund",
    "Enterprise discounts": "enterprise_discount",
    "Service credits": "service_credit",
    "Setup-fee waivers": "setup_fee_waiver",
    "Contract cancellation": "contract_cancellation",
    "Implementation failures": "implementation_failure",
    "Unsupported-feature promises": "unsupported_feature",
    "SLA compensation": "sla_compensation",
    "Vendor-payment exceptions": "vendor_payment",
    "Expense exceptions": "expense_exception",
    "Procurement exceptions": "procurement_exception",
    "Operational exceptions": "operational_exception",
    "Chargebacks": "late_refund",
    "Incident SLA": "sla_compensation",
}

POLICY_CATEGORY_BY_EXCEPTION = {
    "late_refund": "refund",
    "enterprise_discount": "discount",
    "service_credit": "service_credit",
    "setup_fee_waiver": "setup_fee",
    "contract_cancellation": "cancellation",
    "implementation_failure": "refund",
    "unsupported_feature": "cancellation",
    "sla_compensation": "service_credit",
    "vendor_payment": "budget",
    "expense_exception": "budget",
    "procurement_exception": "budget",
    "operational_exception": "escalation",
}

DEPARTMENT_BY_EXCEPTION = {
    "enterprise_discount": "Sales",
    "unsupported_feature": "Sales",
    "implementation_failure": "Engineering",
    "procurement_exception": "Operations",
    "vendor_payment": "Finance",
    "expense_exception": "Finance",
    "contract_cancellation": "Legal",
}

ROOT_CAUSES = (
    "verified internal implementation failure",
    "unsupported feature promised during renewal",
    "delayed refund processing after billing handoff",
    "SLA breach during customer-critical reporting window",
    "vendor invoice mismatch with purchase order",
    "procurement deadline missed due to approval routing",
    "onboarding capacity shortage",
    "manual reconciliation gap in finance operations",
)

CUSTOMER_NAMES = (
    "LumaCart India",
    "BluePeak Foods",
    "Arden Grove Retail",
    "Northstar Robotics",
    "HelioWorks Studios",
    "CopperTrail Finance",
    "VedaHealth Clinics",
    "KiteLine Media",
    "SummitLedger",
    "BrightRiver Labs",
    "OrbitLeaf Markets",
    "CedarGate Services",
)

NOVAFLOW_HERO_CASES = (
    {
        "title": "Outside-window refund after SSO rollout failure",
        "entity_name": "LumaCart India",
        "category_code": "late_refund",
        "root_cause": "verified internal implementation failure",
        "requested_amount": 145000,
        "annual_value": 1800000,
        "decision": "partially_approved",
        "approved_ratio": 0.65,
        "hindsight_tags": ("novaflow_hero", "refund_policy_v3", "outside_window"),
    },
    {
        "title": "Enterprise discount above threshold for strategic renewal",
        "entity_name": "BluePeak Foods",
        "category_code": "enterprise_discount",
        "root_cause": "competitive displacement risk during renewal",
        "requested_amount": 240000,
        "annual_value": 2400000,
        "decision": "approved",
        "approved_ratio": 1.0,
        "hindsight_tags": ("novaflow_hero", "discount_drift", "strategic_account"),
    },
    {
        "title": "Setup-fee waiver after integration work stalled",
        "entity_name": "Arden Grove Retail",
        "category_code": "setup_fee_waiver",
        "root_cause": "verified internal implementation failure",
        "requested_amount": 85000,
        "annual_value": 940000,
        "decision": "approved",
        "approved_ratio": 1.0,
        "hindsight_tags": ("novaflow_hero", "implementation_failure"),
    },
    {
        "title": "Cancellation request tied to unsupported workflow promise",
        "entity_name": "Northstar Robotics",
        "category_code": "contract_cancellation",
        "root_cause": "unsupported feature promised during renewal",
        "requested_amount": 520000,
        "annual_value": 1300000,
        "decision": "escalated",
        "approved_ratio": 0.0,
        "hindsight_tags": ("novaflow_hero", "unsupported_feature", "cfo_review"),
    },
    {
        "title": "Service credit following month-end reporting outage",
        "entity_name": "HelioWorks Studios",
        "category_code": "sla_compensation",
        "root_cause": "SLA breach during customer-critical reporting window",
        "requested_amount": 62000,
        "annual_value": 760000,
        "decision": "partially_approved",
        "approved_ratio": 0.5,
        "hindsight_tags": ("novaflow_hero", "sla_breach"),
    },
)


def generate_dataset(mode: str, seed: int) -> dict[str, Any]:
    if mode not in {MODE_DEMO_SMALL, MODE_FULL_SYNTHETIC}:
        raise ValueError(f"Unsupported synthetic mode: {mode}")

    rng = random.Random(seed)
    Faker.seed(seed)
    fake = Faker()
    fake.seed_instance(seed)
    now = datetime(2026, 6, 13, 9, 0, tzinfo=UTC)

    rows: dict[str, list[dict[str, Any]]] = {}
    artifacts: dict[str, list[dict[str, Any]]] = {
        "personas": [],
        "outcomes": [],
        "conversation_threads": [],
    }

    def add(table: str, row: dict[str, Any], org_id: str | None = None) -> None:
        row.setdefault("synthetic", True)
        rows.setdefault(table, []).append(row)
        row_id = row.get("id")
        owner_org_id = org_id or row.get("organization_id")
        if row_id and owner_org_id and table != "synthetic_data_registry":
            registry_id = deterministic_id_str(owner_org_id, "registry", table, row_id)
            rows.setdefault("synthetic_data_registry", []).append(
                {
                    "id": registry_id,
                    "organization_id": owner_org_id,
                    "table_name": table,
                    "row_id": row_id,
                    "generator_run_id": f"{mode}:{seed}",
                }
            )

    companies = companies_for_mode(mode)
    for company_index, company in enumerate(companies):
        _generate_company(rows, artifacts, add, fake, rng, company, company_index, mode, now)

    _generate_cross_company_benchmarks(rows, add, companies, mode, seed, now)

    return {
        "metadata": {
            "mode": mode,
            "seed": seed,
            "generated_at": now.isoformat(),
            "company_count": len(companies),
            "synthetic": True,
            "notes": [
                "Personas are fictional and embedded as JSON artifacts/facts, not profiles rows.",
                "Human decisions/outcomes are emitted as artifacts and case events because their tables require real profile FKs.",
            ],
        },
        "rows": rows,
        "artifacts": artifacts,
        "counts": {name: len(items) for name, items in rows.items()},
    }


def _generate_company(
    rows: dict[str, list[dict[str, Any]]],
    artifacts: dict[str, list[dict[str, Any]]],
    add: Any,
    fake: Faker,
    rng: random.Random,
    company: CompanyTemplate,
    company_index: int,
    mode: str,
    now: datetime,
) -> None:
    org_id = deterministic_id_str(company.slug, "organization")
    add(
        "organizations",
        {
            "id": org_id,
            "name": company.name,
            "slug": company.slug,
            "industry": company.industry,
            "size": company.size,
            "currency": company.currency,
            "timezone": company.timezone,
            "status": "active",
            "hindsight_bank_id": f"synthetic-bank-{company.slug}",
            "openclaw_enabled": True,
        },
    )

    dept_ids = _generate_departments(add, company, org_id)
    category_ids = _generate_categories(add, company, org_id)
    policies = generate_policies_for_company(fake, company, now)
    policy_versions_by_category = _generate_policies(add, company, org_id, policies)
    personas = generate_personas(fake, company.slug, list(DEPARTMENTS))
    artifacts["personas"].extend(
        {"organization_id": org_id, "company_slug": company.slug, **p.to_dict()} for p in personas
    )

    _generate_feature_flags(add, company, org_id)
    case_count = _case_count_for_company(rng, company, mode)
    cases_for_company: list[dict[str, Any]] = []

    for case_index in range(case_count):
        case_context = _case_context(fake, rng, company, case_index)
        case_rows = _generate_case_bundle(
            add=add,
            artifacts=artifacts,
            fake=fake,
            rng=rng,
            company=company,
            company_index=company_index,
            case_index=case_index,
            case_context=case_context,
            org_id=org_id,
            dept_ids=dept_ids,
            category_ids=category_ids,
            policy_versions_by_category=policy_versions_by_category,
            personas=personas,
            now=now,
        )
        cases_for_company.append(case_rows)

    _generate_sla_rules(add, company, org_id, category_ids)
    _generate_budgets(add, company, org_id, dept_ids, category_ids, cases_for_company, now)
    _generate_learning_artifacts(add, company, org_id, policies, cases_for_company, now)


# Representative urgency tier per category, used to derive a single canonical
# SLA rule per category. The "paused" state is demonstrated by deactivating the
# operational-exception rule so the dashboard has at least one paused SLA.
SLA_URGENCY_BY_CATEGORY = {
    "late_refund": "high",
    "enterprise_discount": "medium",
    "service_credit": "medium",
    "setup_fee_waiver": "low",
    "contract_cancellation": "high",
    "implementation_failure": "high",
    "unsupported_feature": "medium",
    "sla_compensation": "critical",
    "vendor_payment": "medium",
    "expense_exception": "low",
    "procurement_exception": "medium",
    "operational_exception": "medium",
}

SLA_MULTIPLIER = {"low": 1.5, "medium": 1.0, "high": 0.65, "critical": 0.35}


def _generate_sla_rules(
    add: Any, company: CompanyTemplate, org_id: str, category_ids: dict[str, str]
) -> None:
    """One canonical SLA rule per category. ``operational_exception`` is left
    paused (``active=False``) so every org exposes a paused-SLA state."""
    for index, (code, category_id) in enumerate(sorted(category_ids.items())):
        urgency = SLA_URGENCY_BY_CATEGORY.get(code, "medium")
        base = next((c["default_sla_minutes"] for c in EXCEPTION_CATEGORY_DEFS if c["code"] == code), 2880)
        add(
            "sla_rules",
            {
                "id": deterministic_id_str(company.slug, "sla_rule", code),
                "organization_id": org_id,
                "category_id": category_id,
                "urgency": urgency,
                "sla_minutes": int(base * SLA_MULTIPLIER[urgency]),
                "warning_threshold_pct": (0.70, 0.75, 0.80)[index % 3],
                "active": code != "operational_exception",
            },
        )


def _generate_budgets(
    add: Any,
    company: CompanyTemplate,
    org_id: str,
    dept_ids: dict[str, str],
    category_ids: dict[str, str],
    cases: list[dict[str, Any]],
    now: datetime,
) -> None:
    """Per-category Q2-2026 budgets plus per-case spend transactions.

    Applies the spec's budget logic deterministically: each consuming case is a
    ``debit``; some budgets show a released reservation (``credit``); every
    fifth budget is intentionally breached (``spent_amount > budget_amount``)
    with an ``adjustment`` row flagging the overage for finance review.
    """
    period_start, period_end = "2026-04-01", "2026-06-30"
    by_category: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        if case["approved_amount"] and case["status"] in {"approved", "partially_approved", "closed"}:
            by_category.setdefault(case["category_code"], []).append(case)

    for index, code in enumerate(sorted(by_category)):
        category_cases = by_category[code]
        budget_id = deterministic_id_str(company.slug, "budget", code)
        # (transaction_type, amount, case_id, created_at, notes)
        txns: list[tuple[str, float, str | None, str, str]] = [
            (
                "debit",
                round(case["approved_amount"], 2),
                case["id"],
                case["created_at"],
                f"Consumed budget for {case['case_number']} ({code}).",
            )
            for case in category_cases
        ]
        if index % 4 == 1:
            head = category_cases[0]
            txns.append(
                (
                    "credit",
                    round(head["approved_amount"] * 0.25, 2),
                    head["id"],
                    head["created_at"],
                    "Released over-reserved amount back to the budget envelope.",
                )
            )
        spent = round(
            sum(amount if ttype == "debit" else -amount for ttype, amount, _, _, _ in txns if ttype in {"debit", "credit"}),
            2,
        )
        breached = index % 5 == 0
        budget_amount = round(spent * 0.8, 2) if breached else round(spent * 1.6 + 50000, 2)
        if breached:
            txns.append(
                (
                    "adjustment",
                    round(spent - budget_amount, 2),
                    None,
                    now.isoformat(),
                    "Spend exceeded the allocated envelope; flagged for finance review.",
                )
            )
        dept_name = DEPARTMENT_BY_EXCEPTION.get(code, "Customer Success")
        add(
            "exception_budgets",
            {
                "id": budget_id,
                "organization_id": org_id,
                "department_id": dept_ids.get(dept_name),
                "category_id": category_ids[code],
                "period_start": period_start,
                "period_end": period_end,
                "budget_amount": budget_amount,
                "currency": company.currency,
                "spent_amount": spent,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
            },
        )
        for txn_index, (ttype, amount, case_id, created_at, notes) in enumerate(txns):
            add(
                "budget_transactions",
                {
                    "id": deterministic_id_str(company.slug, "budget_txn", code, str(txn_index)),
                    "budget_id": budget_id,
                    "case_id": case_id,
                    "amount": amount,
                    "transaction_type": ttype,
                    "notes": notes,
                    "created_at": created_at,
                },
                org_id=org_id,
            )


def _generate_departments(add: Any, company: CompanyTemplate, org_id: str) -> dict[str, str]:
    dept_ids = {}
    for name in DEPARTMENTS:
        dept_id = deterministic_id_str(company.slug, "department", name)
        dept_ids[name] = dept_id
        add(
            "departments",
            {
                "id": dept_id,
                "organization_id": org_id,
                "name": name,
                "code": "".join(part[0] for part in name.split()).upper(),
            },
        )
    return dept_ids


def _generate_categories(add: Any, company: CompanyTemplate, org_id: str) -> dict[str, str]:
    category_ids = {}
    focus_codes = {CATEGORY_BY_FOCUS.get(focus) for focus in company.exception_focus}
    for cdef in EXCEPTION_CATEGORY_DEFS:
        code = cdef["code"]
        category_id = deterministic_id_str(company.slug, "category", code)
        category_ids[code] = category_id
        focus_note = "core focus" if code in focus_codes else "available taxonomy"
        add(
            "exception_categories",
            {
                "id": category_id,
                "organization_id": org_id,
                "name": cdef["name"],
                "code": code,
                "description": f"{cdef['name']} for {company.name} ({focus_note}).",
                "default_sla_minutes": cdef["default_sla_minutes"],
            },
        )
    return category_ids


def _generate_policies(
    add: Any, company: CompanyTemplate, org_id: str, policies: list[PolicyRow]
) -> dict[str, str]:
    versions_by_category = {}
    for policy in policies:
        policy.organization_id = org_id
        add(
            "policies",
            {
                "id": policy.id,
                "organization_id": org_id,
                "name": policy.name,
                "category": policy.category,
                "status": policy.status,
            },
        )
        active_version_id = None
        for version in policy.versions:
            add(
                "policy_versions",
                {
                    "id": version.id,
                    "policy_id": version.policy_id,
                    "version_label": version.version_label,
                    "content": version.content,
                    "effective_from": version.effective_from,
                    "effective_to": version.effective_to,
                    "status": version.status,
                    "hindsight_document_id": version.hindsight_document_id,
                },
                org_id=org_id,
            )
            if version.status == "active":
                active_version_id = version.id
        if active_version_id:
            versions_by_category[policy.category or "general"] = active_version_id
    return versions_by_category


def _generate_feature_flags(add: Any, company: CompanyTemplate, org_id: str) -> None:
    for flag_key, enabled in (
        ("synthetic_demo_mode", True),
        ("openclaw", True),
        ("voice_artifacts", True),
    ):
        add(
            "feature_flags",
            {
                "id": deterministic_id_str(company.slug, "feature_flag", flag_key),
                "organization_id": org_id,
                "flag_key": flag_key,
                "enabled": enabled,
                "config_json": {"synthetic": True, "company_slug": company.slug},
            },
        )


def _case_count_for_company(rng: random.Random, company: CompanyTemplate, mode: str) -> int:
    if mode == MODE_FULL_SYNTHETIC:
        return rng.randint(*FULL_SYNTHETIC_CASE_RANGE)
    if company.slug == HERO_COMPANY_SLUG:
        return rng.randint(*DEMO_SMALL_HERO_CASE_RANGE)
    return rng.randint(*DEMO_SMALL_OTHER_CASE_RANGE)


def _case_context(fake: Faker, rng: random.Random, company: CompanyTemplate, case_index: int) -> dict[str, Any]:
    if company.slug == HERO_COMPANY_SLUG and case_index < len(NOVAFLOW_HERO_CASES):
        return dict(NOVAFLOW_HERO_CASES[case_index])

    focus = rng.choice(company.exception_focus)
    category_code = CATEGORY_BY_FOCUS.get(focus, "operational_exception")
    root_cause = rng.choice(ROOT_CAUSES)
    customer = rng.choice(CUSTOMER_NAMES)
    title = f"{focus} request for {customer}"
    if category_code == "enterprise_discount":
        title = f"Enterprise discount exception for {customer}"
    elif category_code == "implementation_failure":
        title = f"Implementation failure remediation for {customer}"
    elif category_code == "sla_compensation":
        title = f"SLA compensation review for {customer}"

    amount_floor, amount_ceiling = (15000, 220000)
    if company.currency == "INR":
        amount_floor, amount_ceiling = (25000, 350000)
    requested_amount = rng.randrange(amount_floor, amount_ceiling, 1000)
    annual_value = requested_amount * rng.randint(5, 16)
    decision = _weighted_choice(rng, (("approved", 38), ("partially_approved", 30), ("denied", 17), ("escalated", 15)))
    ratio = {"approved": 1.0, "partially_approved": rng.choice((0.35, 0.5, 0.65, 0.75)), "denied": 0.0, "escalated": 0.0}[decision]
    return {
        "title": title,
        "entity_name": customer,
        "category_code": category_code,
        "root_cause": root_cause,
        "requested_amount": requested_amount,
        "annual_value": annual_value,
        "decision": decision,
        "approved_ratio": ratio,
        "hindsight_tags": (),
    }


def _generate_case_bundle(
    add: Any,
    artifacts: dict[str, list[dict[str, Any]]],
    fake: Faker,
    rng: random.Random,
    company: CompanyTemplate,
    company_index: int,
    case_index: int,
    case_context: dict[str, Any],
    org_id: str,
    dept_ids: dict[str, str],
    category_ids: dict[str, str],
    policy_versions_by_category: dict[str, str],
    personas: list[Persona],
    now: datetime,
) -> dict[str, Any]:
    case_number = f"SYN-{company_index + 1:02d}-{case_index + 1:04d}"
    case_id = deterministic_id_str(company.slug, "case", case_number)
    category_code = case_context["category_code"]
    requested_amount = float(case_context["requested_amount"])
    approved_amount = round(requested_amount * float(case_context["approved_ratio"]), 2)
    status = _status_from_decision(rng, case_context["decision"])
    urgency = _weighted_choice(rng, URGENCY_WEIGHTS)
    created_at = now - timedelta(days=rng.randint(3, 240), hours=rng.randint(0, 20))
    request_date = created_at + timedelta(hours=1)
    transaction_date = request_date - timedelta(days=rng.randint(7, 75))
    sla_minutes = _sla_minutes(category_code, urgency)
    resolved_at = request_date + timedelta(hours=rng.randint(8, 96)) if status in {"closed", "approved", "partially_approved", "denied"} else None
    dept_name = DEPARTMENT_BY_EXCEPTION.get(category_code, "Customer Success")
    policy_category = POLICY_CATEGORY_BY_EXCEPTION.get(category_code, "escalation")
    source = "openclaw" if (case_index % 11 == 0 or company.slug == HERO_COMPANY_SLUG and case_index in {1, 3}) else "web"

    requester = rng.choice(personas_by_role(personas, "requester"))
    assignee_pool = personas_by_role(personas, "customer_success_manager") + personas_by_role(personas, "finance_manager")
    assignee = rng.choice(assignee_pool)
    decider = _select_decider(personas, requested_amount, case_context["decision"])
    recommendation_id = deterministic_id_str(company.slug, "recommendation", case_number, "v1")
    agent_run_id = deterministic_id_str(company.slug, "agent_run", case_number)
    decision_artifact_id = deterministic_id_str(company.slug, "decision_artifact", case_number)
    outcome_artifact_id = deterministic_id_str(company.slug, "outcome_artifact", case_number)
    tags = _hindsight_tags(company, category_code, case_context)

    add(
        "exception_cases",
        {
            "id": case_id,
            "organization_id": org_id,
            "case_number": case_number,
            "category_id": category_ids[category_code],
            "department_id": dept_ids[dept_name],
            "requester_user_id": None,
            "assignee_user_id": None,
            "title": case_context["title"],
            "description": _case_description(company, case_context, requester),
            "entity_name": case_context["entity_name"],
            "requested_amount": requested_amount,
            "currency": company.currency,
            "annual_value": float(case_context["annual_value"]),
            "request_date": request_date.isoformat(),
            "transaction_date": transaction_date.isoformat(),
            "root_cause": case_context["root_cause"],
            "urgency": urgency,
            "status": status,
            "current_policy_version_id": policy_versions_by_category.get(policy_category),
            "current_recommendation_id": recommendation_id,
            "sla_due_at": (request_date + timedelta(minutes=sla_minutes)).isoformat(),
            "resolved_at": resolved_at.isoformat() if resolved_at else None,
            "created_at": created_at.isoformat(),
            "updated_at": (resolved_at or request_date).isoformat(),
            "source": source,
        },
    )

    _generate_case_facts(add, company, org_id, case_id, case_number, case_context, requester, assignee, decider, tags)
    _generate_evidence(add, company, org_id, case_id, case_number, case_context)
    _generate_recommendation(add, company, org_id, case_id, recommendation_id, case_context, approved_amount, tags)
    _generate_agent_run(add, company, org_id, case_id, agent_run_id, tags)
    _generate_events(add, company, org_id, case_id, case_number, requester, decider, case_context, approved_amount, request_date, resolved_at, tags)
    _generate_hindsight_ops(add, company, org_id, case_id, agent_run_id, case_number, tags, request_date)
    _generate_conversation_artifact(artifacts, company, org_id, case_id, case_number, requester, assignee, decider, case_context, tags)
    _generate_outcome_artifact(artifacts, company, org_id, case_id, decision_artifact_id, outcome_artifact_id, decider, case_context, approved_amount, resolved_at or request_date)

    if source == "openclaw":
        _generate_openclaw_session(add, company, org_id, case_id, case_number, case_context, tags)
    if case_index % 9 == 0:
        _generate_voice_session(add, company, org_id, case_id, case_number, case_context, tags)

    return {
        "id": case_id,
        "case_number": case_number,
        "category_code": category_code,
        "policy_category": policy_category,
        "status": status,
        "decision": case_context["decision"],
        "requested_amount": requested_amount,
        "approved_amount": approved_amount,
        "tags": tags,
        "created_at": request_date.isoformat(),
    }


def _generate_case_facts(
    add: Any,
    company: CompanyTemplate,
    org_id: str,
    case_id: str,
    case_number: str,
    case_context: dict[str, Any],
    requester: Persona,
    assignee: Persona,
    decider: Persona,
    tags: list[str],
) -> None:
    facts = {
        "requester_persona": requester.to_dict(),
        "assignee_persona": assignee.to_dict(),
        "decision_persona": decider.to_dict(),
        "hindsight_tags": tags,
        "synthetic_source": {
            "generator": "backend/scripts/synthetic",
            "company_slug": company.slug,
            "synthetic": True,
        },
        "commercial_context": {
            "entity_name": case_context["entity_name"],
            "annual_value": case_context["annual_value"],
            "requested_amount": case_context["requested_amount"],
            "currency": company.currency,
        },
    }
    for key, value in facts.items():
        add(
            "case_facts",
            {
                "id": deterministic_id_str(company.slug, "case_fact", case_number, key),
                "case_id": case_id,
                "key": key,
                "value_json": value,
                "source": "synthetic_generator",
                "confidence": 0.98,
                "verified": True,
            },
            org_id=org_id,
        )


def _generate_evidence(
    add: Any,
    company: CompanyTemplate,
    org_id: str,
    case_id: str,
    case_number: str,
    case_context: dict[str, Any],
) -> None:
    evidence_items = (
        ("contract", "Contract and renewal context"),
        ("support_thread", "Support or implementation notes"),
        ("finance_export", "Billing and amount verification"),
    )
    for evidence_type, title in evidence_items:
        add(
            "case_evidence",
            {
                "id": deterministic_id_str(company.slug, "evidence", case_number, evidence_type),
                "case_id": case_id,
                "file_path": f"synthetic://{company.slug}/{case_number}/{evidence_type}.txt",
                "evidence_type": evidence_type,
                "title": title,
                "extracted_text": f"{title}: {case_context['root_cause']} for {case_context['entity_name']}.",
                "verification_status": "verified",
            },
            org_id=org_id,
        )


def _generate_recommendation(
    add: Any,
    company: CompanyTemplate,
    org_id: str,
    case_id: str,
    recommendation_id: str,
    case_context: dict[str, Any],
    approved_amount: float,
    tags: list[str],
) -> None:
    decision = case_context["decision"]
    recommendation_type = {
        "approved": "approve",
        "partially_approved": "partially_approve",
        "denied": "deny",
        "escalated": "escalate",
    }[decision]
    add(
        "recommendations",
        {
            "id": recommendation_id,
            "case_id": case_id,
            "version": 1,
            "recommendation_type": recommendation_type,
            "recommended_amount": approved_amount if approved_amount else None,
            "conditions_json": _decision_conditions(case_context, approved_amount),
            "confidence": 0.82,
            "reasoning": _decision_reasoning(case_context, approved_amount, company.currency),
            "risk_json": {
                "retention_risk": "high" if case_context["annual_value"] > case_context["requested_amount"] * 10 else "medium",
                "policy_drift_risk": "high" if "discount_drift" in tags else "medium",
                "synthetic": True,
            },
            "provider_summary_json": {"provider": "synthetic", "model": "deterministic-rule-pack", "synthetic": True},
            "hindsight_evidence_json": [{"document_id": f"case:{company.slug}:{case_id}", "tags": tags, "confidence": 0.86}],
        },
        org_id=org_id,
    )


def _generate_agent_run(add: Any, company: CompanyTemplate, org_id: str, case_id: str, agent_run_id: str, tags: list[str]) -> None:
    add(
        "agent_runs",
        {
            "id": agent_run_id,
            "case_id": case_id,
            "run_type": "full_debate",
            "status": "completed",
            "started_at": "2026-06-13T09:00:00+00:00",
            "completed_at": "2026-06-13T09:00:04+00:00",
            "trace_id": f"synthetic-{case_id[:8]}",
            "final_provider": "synthetic",
            "fallback_path_json": [],
            "latency_ms": 4200,
            "token_usage_json": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "synthetic": True},
        },
        org_id=org_id,
    )
    for idx, agent_name in enumerate(("intake", "policy", "finance", "customer_impact", "risk", "precedent", "final_decision")):
        add(
            "agent_outputs",
            {
                "id": deterministic_id_str(company.slug, "agent_output", case_id, agent_name),
                "agent_run_id": agent_run_id,
                "agent_name": agent_name,
                "provider": "synthetic",
                "model": "deterministic-rule-pack",
                "status": "completed",
                "structured_output_json": {"summary": f"Synthetic {agent_name} analysis", "hindsight_tags": tags},
                "latency_ms": 300 + idx * 50,
                "token_usage_json": {"total_tokens": 0, "synthetic": True},
            },
            org_id=org_id,
        )


def _generate_events(
    add: Any,
    company: CompanyTemplate,
    org_id: str,
    case_id: str,
    case_number: str,
    requester: Persona,
    decider: Persona,
    case_context: dict[str, Any],
    approved_amount: float,
    request_date: datetime,
    resolved_at: datetime | None,
    tags: list[str],
) -> None:
    event_specs = [
        ("case_submitted", "user", requester.id, request_date),
        ("agent_analysis_completed", "agent", "synthetic_orchestrator", request_date + timedelta(hours=2)),
        ("decision_recorded", "user", decider.id, resolved_at or request_date + timedelta(days=1)),
    ]
    if resolved_at:
        event_specs.append(("outcome_recorded", "system", "synthetic_generator", resolved_at + timedelta(days=30)))
    for event_type, actor_type, actor_id, created_at in event_specs:
        add(
            "case_events",
            {
                "id": deterministic_id_str(company.slug, "case_event", case_number, event_type),
                "case_id": case_id,
                "organization_id": org_id,
                "event_type": event_type,
                "actor_type": actor_type,
                "actor_id": actor_id,
                "payload_json": {
                    "decision": case_context["decision"],
                    "approved_amount": approved_amount,
                    "hindsight_tags": tags,
                    "synthetic": True,
                },
                "created_at": created_at.isoformat(),
            },
        )


def _generate_hindsight_ops(
    add: Any,
    company: CompanyTemplate,
    org_id: str,
    case_id: str,
    agent_run_id: str,
    case_number: str,
    tags: list[str],
    request_date: datetime,
) -> None:
    for offset, operation_type in enumerate(("recall", "retain", "reflect")):
        document_id = f"case:{company.slug}:{case_number}:{operation_type}"
        add(
            "hindsight_operations",
            {
                "id": deterministic_id_str(company.slug, "hindsight", case_number, operation_type),
                "organization_id": org_id,
                "case_id": case_id,
                "agent_run_id": agent_run_id,
                "operation_type": operation_type,
                "document_id": document_id,
                "bank_id": f"synthetic-bank-{company.slug}",
                "status": "completed",
                "request_json": {"tags": tags, "synthetic": True},
                "response_json": {"document_id": document_id, "memory_tags": tags, "synthetic": True},
                "latency_ms": 120 + offset * 20,
                "created_at": (request_date + timedelta(minutes=offset * 20)).isoformat(),
            },
        )


def _generate_conversation_artifact(
    artifacts: dict[str, list[dict[str, Any]]],
    company: CompanyTemplate,
    org_id: str,
    case_id: str,
    case_number: str,
    requester: Persona,
    assignee: Persona,
    decider: Persona,
    case_context: dict[str, Any],
    tags: list[str],
) -> None:
    artifacts["conversation_threads"].append(
        {
            "id": deterministic_id_str(company.slug, "conversation", case_number),
            "organization_id": org_id,
            "case_id": case_id,
            "case_number": case_number,
            "channel": "synthetic_internal_thread",
            "messages": [
                {"speaker": requester.to_dict(), "text": f"Requesting review: {case_context['title']}."},
                {"speaker": assignee.to_dict(), "text": "Evidence is attached and mapped to the active policy version."},
                {"speaker": decider.to_dict(), "text": _decision_reasoning(case_context, case_context["requested_amount"] * case_context["approved_ratio"], company.currency)},
            ],
            "hindsight_tags": tags,
            "synthetic": True,
        }
    )


def _generate_outcome_artifact(
    artifacts: dict[str, list[dict[str, Any]]],
    company: CompanyTemplate,
    org_id: str,
    case_id: str,
    decision_artifact_id: str,
    outcome_artifact_id: str,
    decider: Persona,
    case_context: dict[str, Any],
    approved_amount: float,
    decision_date: datetime,
) -> None:
    retained = case_context["decision"] in {"approved", "partially_approved"} and case_context["approved_ratio"] >= 0.5
    artifacts["outcomes"].append(
        {
            "id": outcome_artifact_id,
            "decision_artifact_id": decision_artifact_id,
            "organization_id": org_id,
            "case_id": case_id,
            "decision_type": case_context["decision"],
            "approved_amount": approved_amount,
            "decided_by_persona": decider.to_dict(),
            "decided_at": decision_date.isoformat(),
            "actual_outcome": "customer_retained" if retained else "no_retention_change",
            "outcome_date": (decision_date + timedelta(days=30)).isoformat(),
            "financial_impact": -approved_amount if approved_amount else 0,
            "notes": "Synthetic outcome artifact; not inserted into FK-backed outcomes table without a real profile.",
            "synthetic": True,
        }
    )


def _generate_openclaw_session(
    add: Any,
    company: CompanyTemplate,
    org_id: str,
    case_id: str,
    case_number: str,
    case_context: dict[str, Any],
    tags: list[str],
) -> None:
    add(
        "openclaw_sessions",
        {
            "id": deterministic_id_str(company.slug, "openclaw", case_number),
            "organization_id": org_id,
            "external_session_id": f"oc-synth-{company.slug}-{case_number.lower()}",
            "channel": "chat",
            "linked_case_id": case_id,
            "action_type": "create_draft_case",
            "status": "closed",
            "metadata_json": {
                "title": case_context["title"],
                "hindsight_tags": tags,
                "synthetic": True,
                "guardrail": "OpenClaw created intake context only; no final decision was made.",
            },
        },
    )


def _generate_voice_session(
    add: Any,
    company: CompanyTemplate,
    org_id: str,
    case_id: str,
    case_number: str,
    case_context: dict[str, Any],
    tags: list[str],
) -> None:
    add(
        "voice_sessions",
        {
            "id": deterministic_id_str(company.slug, "voice", case_number),
            "organization_id": org_id,
            "user_id": None,
            "case_id": case_id,
            "external_session_id": f"voice-synth-{company.slug}-{case_number.lower()}",
            "agent_id": "synthetic-elevenlabs-agent",
            "status": "completed",
            "consent_given": True,
            "transcript_json": [
                {"role": "requester", "text": f"I need a decision on {case_context['title']}."},
                {"role": "assistant", "text": "I can summarize policy context and capture facts, but a human approver decides."},
            ],
            "started_at": "2026-06-13T09:00:00+00:00",
            "ended_at": "2026-06-13T09:04:00+00:00",
        },
    )


def _generate_learning_artifacts(
    add: Any,
    company: CompanyTemplate,
    org_id: str,
    policies: list[PolicyRow],
    cases: list[dict[str, Any]],
    now: datetime,
) -> None:
    if not cases:
        return
    refund_policy = next((p for p in policies if p.category == "refund"), policies[0])
    refund_version = next((v for v in refund_policy.versions if v.status == "active"), refund_policy.versions[-1])
    affected = [c["id"] for c in cases if c["category_code"] in {"late_refund", "implementation_failure"}][:8]
    if affected:
        add(
            "policy_drift_findings",
            {
                "id": deterministic_id_str(company.slug, "policy_drift", "refund_or_implementation"),
                "organization_id": org_id,
                "policy_id": refund_policy.id,
                "policy_version_id": refund_version.id,
                "finding_type": "approval_pattern_exceeds_policy_baseline",
                "description": f"{company.name} shows repeated approvals tied to implementation or refund exceptions.",
                "evidence_json": [{"case_id": cid, "tags": ["synthetic", company.slug]} for cid in affected],
                "affected_case_ids_json": affected,
                "severity": "high" if company.slug == HERO_COMPANY_SLUG else "medium",
                "status": "open",
                "detected_at": now.isoformat(),
            },
        )

    cluster_cases = [c for c in cases if c["category_code"] == cases[0]["category_code"]][:6]
    add(
        "repeated_exception_clusters",
        {
            "id": deterministic_id_str(company.slug, "cluster", cases[0]["category_code"]),
            "organization_id": org_id,
            "cluster_key": f"{company.slug}:{cases[0]['category_code']}",
            "title": f"Repeated {cases[0]['category_code']} exceptions",
            "description": f"Deterministic cluster for {company.name} synthetic demo data.",
            "root_cause": "repeated operational exception pattern",
            "case_ids_json": [c["id"] for c in cluster_cases],
            "occurrence_count": len(cluster_cases),
            "first_seen_at": min(c["created_at"] for c in cluster_cases),
            "last_seen_at": max(c["created_at"] for c in cluster_cases),
            "status": "open",
        },
    )

    if len(cases) >= 2:
        add(
            "memory_contradictions",
            {
                "id": deterministic_id_str(company.slug, "memory_contradiction", "case_pair"),
                "organization_id": org_id,
                "memory_id_a": f"case:{company.slug}:{cases[0]['case_number']}:retain",
                "memory_id_b": f"case:{company.slug}:{cases[1]['case_number']}:retain",
                "case_id_a": cases[0]["id"],
                "case_id_b": cases[1]["id"],
                "contradiction_type": "different_outcomes_for_similar_context",
                "description": "Synthetic contrast pair for Hindsight recall and Reflect demonstrations.",
                "severity": "medium",
                "status": "open",
                "detected_at": now.isoformat(),
            },
        )

    for index, case in enumerate(cases[:3]):
        add(
            "training_scenarios",
            {
                "id": deterministic_id_str(company.slug, "training_scenario", case["case_number"]),
                "organization_id": org_id,
                "source_case_id": case["id"],
                "category_id": deterministic_id_str(company.slug, "category", case["category_code"]),
                "title": f"Training review: {case['case_number']}",
                "description": "Synthetic training scenario derived from a generated exception case.",
                "scenario_json": {"case_number": case["case_number"], "hindsight_tags": case["tags"], "synthetic": True},
                "correct_decision_json": {"decision": case["decision"], "approved_amount": case["approved_amount"]},
                "difficulty": ("easy", "medium", "hard")[index % 3],
                "active": True,
            },
        )


def _generate_cross_company_benchmarks(
    rows: dict[str, list[dict[str, Any]]],
    add: Any,
    companies: tuple[CompanyTemplate, ...],
    mode: str,
    seed: int,
    now: datetime,
) -> None:
    cases = rows.get("exception_cases", [])
    for company in companies:
        company_cases = [c for c in cases if c["organization_id"] == deterministic_id_str(company.slug, "organization")]
        if not company_cases:
            continue
        approved = [c for c in company_cases if c["status"] in {"approved", "partially_approved", "closed"}]
        metric_value = round(len(approved) / len(company_cases), 4)
        add(
            "benchmark_cohorts",
            {
                "id": deterministic_id_str("benchmark", mode, str(seed), company.slug),
                "cohort_key": f"synthetic:{mode}:{company.industry}:{company.size}",
                "industry": company.industry,
                "organization_size": company.size,
                "category": "all",
                "metric_name": "approval_or_closure_rate",
                "metric_value": metric_value,
                "percentile_data_json": {"p50": metric_value, "p75": min(metric_value + 0.12, 1.0), "synthetic": True},
                "period_start": "2026-01-01",
                "period_end": now.date().isoformat(),
                "sample_size": len(company_cases),
            },
            org_id=deterministic_id_str(company.slug, "organization"),
        )


def _select_decider(personas: list[Persona], amount: float, decision: str) -> Persona:
    if decision == "escalated" or amount >= 100000:
        return personas_by_role(personas, "cfo")[0]
    if amount >= 50000:
        return personas_by_role(personas, "finance_manager")[0]
    return personas_by_role(personas, "department_head")[0]


def _case_description(company: CompanyTemplate, case_context: dict[str, Any], requester: Persona) -> str:
    return (
        f"{requester.name} requested a {company.currency} {case_context['requested_amount']:.0f} "
        f"exception for {case_context['entity_name']} because of {case_context['root_cause']}."
    )


def _status_from_decision(rng: random.Random, decision: str) -> str:
    if decision == "approved":
        return rng.choice(("approved", "closed"))
    if decision == "partially_approved":
        return rng.choice(("partially_approved", "closed"))
    if decision == "denied":
        return "denied"
    return rng.choice(("escalated", "pending_decision"))


def _weighted_choice(rng: random.Random, weights: tuple[tuple[str, int], ...]) -> str:
    total = sum(weight for _, weight in weights)
    pick = rng.randint(1, total)
    cursor = 0
    for value, weight in weights:
        cursor += weight
        if pick <= cursor:
            return value
    return weights[-1][0]


def _sla_minutes(category_code: str, urgency: str) -> int:
    base = next((c["default_sla_minutes"] for c in EXCEPTION_CATEGORY_DEFS if c["code"] == category_code), 2880)
    multiplier = {"low": 1.5, "medium": 1.0, "high": 0.65, "critical": 0.35}[urgency]
    return int(base * multiplier)


def _hindsight_tags(company: CompanyTemplate, category_code: str, case_context: dict[str, Any]) -> list[str]:
    tags = ["synthetic", "exceptionos", company.slug, category_code]
    tags.extend(case_context.get("hindsight_tags", ()))
    if "implementation failure" in case_context["root_cause"]:
        tags.append("implementation_failure")
    return sorted(set(tags))


def _decision_conditions(case_context: dict[str, Any], approved_amount: float) -> list[dict[str, Any]]:
    if approved_amount <= 0:
        return [{"condition": "Document denial rationale and offer remediation path", "synthetic": True}]
    return [
        {"condition": "Attach verified evidence before payment or credit processing", "synthetic": True},
        {"condition": "Review account outcome after 30 days", "synthetic": True},
    ]


def _decision_reasoning(case_context: dict[str, Any], approved_amount: float, currency: str) -> str:
    if approved_amount <= 0:
        return f"Recommend escalation or denial because evidence does not yet justify the requested exception for {case_context['entity_name']}."
    return (
        f"Recommend {currency} {approved_amount:.0f} based on {case_context['root_cause']}, "
        f"commercial context, and comparable synthetic Hindsight precedents."
    )
