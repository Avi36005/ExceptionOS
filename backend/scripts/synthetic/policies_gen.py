"""Policy + policy_version generation.

Each company gets 4-7 policy categories. NovaFlow (the hero company) gets
the full 7-policy set described in the synthetic-data spec, including a
versioned Refund Policy (v1 superseded, v2 historical, v3 current) whose
v3 content matches the spec's "NovaFlow Refund Policy Example".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from faker import Faker

from scripts.synthetic.config import CompanyTemplate
from scripts.synthetic.ids import deterministic_id_str

UTC = timezone.utc


@dataclass
class PolicyVersionRow:
    id: str
    policy_id: str
    version_label: str
    content: str
    effective_from: str | None
    effective_to: str | None
    status: str
    hindsight_document_id: str | None = None
    structured: dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyRow:
    id: str
    organization_id: str
    name: str
    category: str
    status: str
    versions: list[PolicyVersionRow] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Generic policy catalogue (used for non-hero companies and as a fallback)
# ---------------------------------------------------------------------------

GENERIC_POLICY_DEFS: tuple[dict, ...] = (
    {"name": "Refund Policy", "category": "refund"},
    {"name": "Discount Policy", "category": "discount"},
    {"name": "Service Credit Policy", "category": "service_credit"},
    {"name": "Setup Fee Policy", "category": "setup_fee"},
    {"name": "Contract Cancellation Policy", "category": "cancellation"},
    {"name": "Escalation Authority Policy", "category": "escalation"},
    {"name": "Exception Budget Policy", "category": "budget"},
)

NOVAFLOW_REFUND_V3_CONTENT = """NovaFlow Refund Policy — Version 3 (Current)

1. Standard refund window: 30 days from the original transaction date.
2. Refund requests submitted outside the 30-day window MAY be considered
   only where internal implementation failure (verified by Engineering) is
   the documented cause of the delay.
3. A partial refund SHOULD be considered when usable service was delivered
   for part of the affected period, proportional to the unusable portion.
4. Refunds greater than ₹50,000 require Finance Director approval.
5. Refunds greater than ₹1,00,000 require CFO approval.
6. Full refunds requested outside the 30-day window require documented
   reasoning covering: root cause, evidence of internal fault, and customer
   commercial context (annual contract value, expansion potential, churn risk).
7. Every approved decision outcome must be reviewed after 30 days to confirm
   customer retention, resolution time, and whether the refund amount was
   appropriate.

Allowed exception paths: outside-window refund with verified internal fault;
partial refund for partial service delivery; full refund with CFO sign-off
for high-value strategic accounts.

Required evidence: transaction date, support/engineering confirmation of
fault, service-delivery logs, customer commercial profile (ACV, renewal date,
expansion pipeline).

Department scope: Customer Success, Finance, Engineering (fault verification).

Prohibited actions: approving refunds above ₹1,00,000 without CFO sign-off;
approving outside-window refunds with no documented root cause.
"""

NOVAFLOW_REFUND_V2_CONTENT = """NovaFlow Refund Policy — Version 2 (Historical, superseded by v3)

1. Standard refund window: 30 days from the original transaction date.
2. Refunds outside the 30-day window are RARE and require Finance Director
   sign-off regardless of amount.
3. Partial refunds for partially delivered service were considered only on
   a case-by-case basis with no formal proportionality guidance.
4. Refunds greater than ₹75,000 require CFO approval.
5. No formal 30-day outcome review requirement existed under this version.

This version was superseded after Q2 due to a high volume of outside-window
refund requests caused by a sustained integration-failure incident affecting
multiple customers (see policy drift findings).
"""

NOVAFLOW_REFUND_V1_CONTENT = """NovaFlow Refund Policy — Version 1 (Historical, superseded)

1. Refunds are only available within 14 days of the original transaction.
2. Refunds outside this window are not supported under any circumstances.
3. Partial refunds are not offered.
4. All refunds above ₹25,000 require CFO approval regardless of cause.

This initial version proved too rigid in practice — see Version 2 and
Version 3 for the evolution driven by real implementation-failure incidents.
"""

NOVAFLOW_POLICY_DEFS: tuple[dict, ...] = (
    {
        "name": "Refund Policy",
        "category": "refund",
        "versions": [
            {"label": "v1", "status": "archived", "content": NOVAFLOW_REFUND_V1_CONTENT},
            {"label": "v2", "status": "archived", "content": NOVAFLOW_REFUND_V2_CONTENT},
            {"label": "v3", "status": "active", "content": NOVAFLOW_REFUND_V3_CONTENT},
        ],
    },
    {
        "name": "Discount Policy",
        "category": "discount",
        "versions": [
            {
                "label": "v1",
                "status": "archived",
                "content": (
                    "NovaFlow Discount Policy — Version 1 (Historical)\n\n"
                    "Standard discounts up to 15% may be approved by Sales Managers. "
                    "Discounts above 15% require Finance approval. "
                    "Enterprise deals (ACV > ₹10,00,000) follow the same threshold."
                ),
            },
            {
                "label": "v2",
                "status": "active",
                "content": (
                    "NovaFlow Discount Policy — Version 2 (Current)\n\n"
                    "1. Discounts up to 15% may be approved by Sales Managers without "
                    "additional sign-off.\n"
                    "2. Discounts above 15% require Finance Director approval and must "
                    "document the competitive or strategic justification.\n"
                    "3. Enterprise deals (ACV > ₹10,00,000) with discounts above 20% "
                    "additionally require CFO approval.\n"
                    "4. Multi-year commitments may receive an additional 5% loyalty "
                    "discount stacked on top of the above, subject to the same approval "
                    "thresholds applied to the combined discount.\n\n"
                    "Note: Reflect analysis has identified that actual enterprise "
                    "discounts frequently fall in the 18-25% range — see policy drift "
                    "findings for v2."
                ),
            },
        ],
    },
    {
        "name": "Service Credit Policy",
        "category": "service_credit",
        "versions": [
            {
                "label": "v1",
                "status": "active",
                "content": (
                    "NovaFlow Service Credit Policy — Version 1 (Current)\n\n"
                    "1. Customers experiencing a verified outage exceeding the SLA "
                    "uptime commitment are eligible for service credits proportional "
                    "to downtime duration.\n"
                    "2. Outages between 4 and 12 hours: 1 month of service credit.\n"
                    "3. Outages exceeding 12 hours: up to 2 months of service credit, "
                    "subject to Customer Success Manager and Finance Manager approval.\n"
                    "4. Service credits do not constitute a cash refund and must be "
                    "applied to a future invoice within 6 months."
                ),
            },
        ],
    },
    {
        "name": "Setup Fee Policy",
        "category": "setup_fee",
        "versions": [
            {
                "label": "v1",
                "status": "active",
                "content": (
                    "NovaFlow Setup Fee Policy — Version 1 (Current)\n\n"
                    "1. Setup fees are non-refundable once onboarding has commenced.\n"
                    "2. Exception: where onboarding could not be completed due to a "
                    "verified internal implementation failure, the setup fee MAY be "
                    "waived or refunded, subject to Finance Manager approval.\n"
                    "3. Reflect analysis shows setup fees were waived or refunded in "
                    "approximately 40% of failed-implementation cases — see policy "
                    "drift findings."
                ),
            },
        ],
    },
    {
        "name": "Contract Cancellation Policy",
        "category": "cancellation",
        "versions": [
            {
                "label": "v1",
                "status": "active",
                "content": (
                    "NovaFlow Contract Cancellation Policy — Version 1 (Current)\n\n"
                    "1. Customers may cancel with 30 days' written notice for "
                    "convenience after the initial 12-month term.\n"
                    "2. Early cancellation due to a verified, sustained internal "
                    "implementation failure (>30 days unresolved) may be approved "
                    "without early-termination penalty, subject to CFO approval if the "
                    "remaining contract value exceeds ₹5,00,000.\n"
                    "3. All cancellation requests must be logged with root-cause "
                    "analysis and an offer of remediation (service credit, partial "
                    "refund, or plan downgrade) before processing."
                ),
            },
        ],
    },
    {
        "name": "Escalation Authority Policy",
        "category": "escalation",
        "versions": [
            {
                "label": "v1",
                "status": "active",
                "content": (
                    "NovaFlow Escalation Authority Policy — Version 1 (Current)\n\n"
                    "1. Exceptions valued up to ₹25,000 may be decided by a Team Lead.\n"
                    "2. Exceptions valued ₹25,001 - ₹50,000 require a Department "
                    "Manager.\n"
                    "3. Exceptions valued ₹50,001 - ₹1,00,000 require the Finance "
                    "Director.\n"
                    "4. Exceptions valued above ₹1,00,000 require CFO approval.\n"
                    "5. Any exception flagged 'critical' urgency is escalated one "
                    "level above its amount-based threshold."
                ),
            },
        ],
    },
    {
        "name": "Exception Budget Policy",
        "category": "budget",
        "versions": [
            {
                "label": "v1",
                "status": "active",
                "content": (
                    "NovaFlow Exception Budget Policy — Version 1 (Current)\n\n"
                    "1. Each department is allocated a monthly exception budget "
                    "covering refunds, service credits, and discounts beyond standard "
                    "authority.\n"
                    "2. Approved exceptions debit the owning department's budget; "
                    "denied or reduced requests release any reserved amount.\n"
                    "3. Departments approaching 80% of their monthly budget should "
                    "flag pending high-value cases for early Finance review.\n"
                    "4. Exceeding 100% of the monthly budget requires CFO "
                    "acknowledgement before further exceptions in that category may be "
                    "approved that month."
                ),
            },
        ],
    },
)


def _policy_version_id(org_slug: str, policy_name: str, label: str) -> str:
    return deterministic_id_str(org_slug, "policy_version", policy_name, label)


def _policy_id(org_slug: str, policy_name: str) -> str:
    return deterministic_id_str(org_slug, "policy", policy_name)


def _generic_version_content(fake: Faker, company: CompanyTemplate, policy_name: str, label: str, status: str) -> str:
    currency = company.currency
    focus = ", ".join(company.exception_focus[:3]) if company.exception_focus else "operational exceptions"
    tag = "Current" if status == "active" else "Historical (superseded)"
    return (
        f"{company.name} {policy_name} — {label.upper()} ({tag})\n\n"
        f"1. Standard requests are handled within the team's normal authority "
        f"and do not require escalation.\n"
        f"2. Exceptions related to {focus} above the standard threshold require "
        f"Finance Manager review.\n"
        f"3. Amounts above {currency} 50,000 require Finance Director approval; "
        f"amounts above {currency} 100,000 require CFO approval.\n"
        f"4. All exception decisions must document root cause, evidence quality, "
        f"and expected customer or vendor impact.\n"
        f"5. Decision outcomes should be reviewed after 30 days to confirm the "
        f"expected impact materialised."
    )


def generate_policies_for_company(
    fake: Faker, company: CompanyTemplate, now: datetime
) -> list[PolicyRow]:
    """Generate the full policy + policy_version set for one company."""
    policies: list[PolicyRow] = []

    defs = NOVAFLOW_POLICY_DEFS if company.slug == "novaflow" else None

    if defs is not None:
        for pdef in defs:
            policy_id = _policy_id(company.slug, pdef["name"])
            versions: list[PolicyVersionRow] = []
            n_versions = len(pdef["versions"])
            for idx, vdef in enumerate(pdef["versions"]):
                # Spread effective dates across the past ~18 months
                months_ago_start = (n_versions - idx) * 6
                months_ago_end = (n_versions - idx - 1) * 6
                effective_from = now - timedelta(days=30 * months_ago_start)
                effective_to = (
                    now - timedelta(days=30 * months_ago_end) if vdef["status"] != "active" else None
                )
                versions.append(
                    PolicyVersionRow(
                        id=_policy_version_id(company.slug, pdef["name"], vdef["label"]),
                        policy_id=policy_id,
                        version_label=vdef["label"],
                        content=vdef["content"],
                        effective_from=effective_from.isoformat(),
                        effective_to=effective_to.isoformat() if effective_to else None,
                        status=vdef["status"],
                        hindsight_document_id=f"policy:{company.slug}:{pdef['category']}:{vdef['label']}",
                    )
                )
            policies.append(
                PolicyRow(
                    id=policy_id,
                    organization_id="",  # filled in by caller
                    name=pdef["name"],
                    category=pdef["category"],
                    status="active",
                    versions=versions,
                )
            )
        return policies

    # Non-hero companies: 4-7 policies drawn from the generic catalogue,
    # each with a current version and roughly half with a superseded
    # historical version too.
    n_policies = fake.random_int(min=4, max=len(GENERIC_POLICY_DEFS))
    chosen = fake.random_elements(
        elements=GENERIC_POLICY_DEFS, length=n_policies, unique=True
    )
    for i, pdef in enumerate(chosen):
        policy_id = _policy_id(company.slug, pdef["name"])
        versions: list[PolicyVersionRow] = []

        has_history = i % 2 == 0
        if has_history:
            old_from = now - timedelta(days=540)
            old_to = now - timedelta(days=180)
            versions.append(
                PolicyVersionRow(
                    id=_policy_version_id(company.slug, pdef["name"], "v1"),
                    policy_id=policy_id,
                    version_label="v1",
                    content=_generic_version_content(fake, company, pdef["name"], "v1", "archived"),
                    effective_from=old_from.isoformat(),
                    effective_to=old_to.isoformat(),
                    status="archived",
                    hindsight_document_id=f"policy:{company.slug}:{pdef['category']}:v1",
                )
            )
            current_label = "v2"
        else:
            current_label = "v1"

        current_from = now - timedelta(days=180)
        versions.append(
            PolicyVersionRow(
                id=_policy_version_id(company.slug, pdef["name"], current_label),
                policy_id=policy_id,
                version_label=current_label,
                content=_generic_version_content(fake, company, pdef["name"], current_label, "active"),
                effective_from=current_from.isoformat(),
                effective_to=None,
                status="active",
                hindsight_document_id=f"policy:{company.slug}:{pdef['category']}:{current_label}",
            )
        )
        policies.append(
            PolicyRow(
                id=policy_id,
                organization_id="",
                name=pdef["name"],
                category=pdef["category"],
                status="active",
                versions=versions,
            )
        )
    return policies
