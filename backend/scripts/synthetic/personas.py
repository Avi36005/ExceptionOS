"""Fictional internal-user personas per company.

Per the synthetic-data spec, every company gets a roster of fictional
internal users (requesters, customer-success managers, sales reps, finance
managers, policy admins, department heads, CFO, auditors, trainees).

These personas are *not* written to ``profiles`` (that table has a hard FK
to ``auth.users`` which we cannot create from a service-role script without
a real Supabase Auth signup). Instead each persona gets a stable synthetic
UUID (used only inside JSON payloads / Hindsight metadata / case_facts —
never as a FK value into `profiles`/`organization_memberships`) plus a
fictional name and an @example.com-style email, and is embedded as
descriptive JSON wherever the data model calls for "users".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from faker import Faker

from scripts.synthetic.config import PERSONA_ROLES
from scripts.synthetic.ids import deterministic_id_str

COMMUNICATION_STYLES = (
    "direct and concise",
    "diplomatic and detail-oriented",
    "data-driven and skeptical",
    "empathetic and customer-first",
    "terse and policy-focused",
    "collaborative and exploratory",
)

DECISION_PATTERNS = (
    "tends to approve when evidence is verified",
    "leans conservative; prefers partial approvals",
    "escalates anything above their authority without hesitation",
    "weighs customer retention heavily over strict policy",
    "applies policy literally, rarely grants exceptions",
    "balances financial impact against relationship value",
)


@dataclass
class Persona:
    id: str
    name: str
    email: str
    role: str
    department: str
    decision_authority: str
    communication_style: str
    historical_decision_pattern: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "department": self.department,
            "decision_authority": self.decision_authority,
            "communication_style": self.communication_style,
            "historical_decision_pattern": self.historical_decision_pattern,
            "synthetic": True,
        }


_AUTHORITY_BY_ROLE = {
    "requester": "none (submits requests only)",
    "customer_success_manager": "up to small service credits",
    "sales_representative": "none (recommends discounts only)",
    "finance_manager": "up to mid-tier refunds and discounts",
    "policy_administrator": "policy authoring; no case decisions",
    "department_head": "department-level approvals",
    "cfo": "full financial authority, all amounts",
    "auditor": "read-only; no approval authority",
    "trainee": "none (training mode only)",
}


def generate_personas(fake: Faker, org_slug: str, departments: list[str]) -> list[Persona]:
    """Generate one persona per role defined in ``PERSONA_ROLES``, plus a
    couple of extra requesters/customer-success folks so conversations have
    a believable cast.
    """
    personas: list[Persona] = []
    role_counts = {
        "requester": 3,
        "customer_success_manager": 2,
        "sales_representative": 2,
        "finance_manager": 1,
        "policy_administrator": 1,
        "department_head": 2,
        "cfo": 1,
        "auditor": 1,
        "trainee": 1,
    }

    for role in PERSONA_ROLES:
        count = role_counts.get(role, 1)
        for i in range(count):
            name = fake.name()
            slug_name = name.lower().replace(" ", ".").replace("'", "")
            email = f"{slug_name}@{org_slug}.example.com"
            department = fake.random_element(departments) if departments else "General"
            persona = Persona(
                id=deterministic_id_str(org_slug, "persona", role, str(i)),
                name=name,
                email=email,
                role=role,
                department=department,
                decision_authority=_AUTHORITY_BY_ROLE.get(role, "none"),
                communication_style=fake.random_element(COMMUNICATION_STYLES),
                historical_decision_pattern=fake.random_element(DECISION_PATTERNS),
            )
            personas.append(persona)
    return personas


def personas_by_role(personas: list[Persona], role: str) -> list[Persona]:
    return [p for p in personas if p.role == role]
