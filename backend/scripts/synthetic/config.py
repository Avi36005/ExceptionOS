"""Configuration, constants, and environment loading for the ExceptionOS
synthetic-data system.

This module never hardcodes secrets. It loads ``backend/.env`` via
python-dotenv (if present) so the generator/loader can read the same
environment variable *names* the backend uses (``SUPABASE_URL``,
``SUPABASE_SERVICE_ROLE_KEY``, ``HINDSIGHT_API_KEY``, ``HINDSIGHT_BASE_URL``,
``EXCEPTIONOS_SYNTHETIC_SEED``) at runtime.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# .env loading
# ---------------------------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parents[2]  # backend/
ENV_PATH = BACKEND_DIR / ".env"


def load_env() -> None:
    """Load ``backend/.env`` into ``os.environ`` if python-dotenv is
    available and the file exists. Never prints or returns secret values.
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH, override=False)


def get_env(name: str, default: str = "") -> str:
    """Read an environment variable by name (no secrets hardcoded)."""
    return os.environ.get(name, default)


# ---------------------------------------------------------------------------
# Generation modes
# ---------------------------------------------------------------------------

MODE_DEMO_SMALL = "demo-small"
MODE_FULL_SYNTHETIC = "full-synthetic"

DEFAULT_MODE = MODE_DEMO_SMALL

# DEMO_SMALL: 12 companies, hero gets 30-40 cases, others 10-15 each
DEMO_SMALL_HERO_CASE_RANGE = (30, 40)
DEMO_SMALL_OTHER_CASE_RANGE = (10, 15)
DEMO_SMALL_COMPANY_COUNT = 12

# FULL_SYNTHETIC: 15 companies, 40-60 cases each
FULL_SYNTHETIC_COMPANY_COUNT = 15
FULL_SYNTHETIC_CASE_RANGE = (40, 60)

MIN_COMPANIES = 10
MAX_COMPANIES = 15


def default_seed() -> int:
    """Deterministic seed, overridable via EXCEPTIONOS_SYNTHETIC_SEED."""
    raw = get_env("EXCEPTIONOS_SYNTHETIC_SEED", "2026")
    try:
        return int(raw)
    except ValueError:
        return 2026


# ---------------------------------------------------------------------------
# Currency / locale per company (fictional companies, plausible currencies)
# ---------------------------------------------------------------------------

# NovaFlow is the hero company and MUST use INR per the synthetic-data spec.
HERO_COMPANY_SLUG = "novaflow"

# ---------------------------------------------------------------------------
# Company roster (12 suggested companies from the spec; FULL_SYNTHETIC adds 3 more)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CompanyTemplate:
    name: str
    slug: str
    industry: str
    size: str
    currency: str
    timezone: str
    exception_focus: tuple[str, ...] = field(default_factory=tuple)


COMPANY_TEMPLATES: tuple[CompanyTemplate, ...] = (
    CompanyTemplate(
        name="NovaFlow Systems",
        slug="novaflow",
        industry="B2B Workflow SaaS",
        size="201-500",
        currency="INR",
        timezone="Asia/Kolkata",
        exception_focus=(
            "Late refunds", "Enterprise discounts", "Service credits",
            "Setup-fee waivers", "Contract cancellation",
            "Implementation failures", "Unsupported-feature promises",
            "SLA compensation",
        ),
    ),
    CompanyTemplate(
        name="CargoNest Logistics",
        slug="cargonest",
        industry="Logistics and Freight",
        size="501-1000",
        currency="INR",
        timezone="Asia/Kolkata",
        exception_focus=("Late deliveries", "Damage claims", "Vendor-payment exceptions", "SLA compensation"),
    ),
    CompanyTemplate(
        name="CloudHarbor Security",
        slug="cloudharbor",
        industry="Cybersecurity SaaS",
        size="51-200",
        currency="USD",
        timezone="America/New_York",
        exception_focus=("Enterprise discounts", "Service credits", "Contract cancellation", "Incident SLA"),
    ),
    CompanyTemplate(
        name="RetailOrbit Commerce",
        slug="retailorbit",
        industry="E-commerce Platform",
        size="201-500",
        currency="USD",
        timezone="America/Chicago",
        exception_focus=("Late refunds", "Chargebacks", "Vendor-payment exceptions", "Procurement exceptions"),
    ),
    CompanyTemplate(
        name="BuildSphere Projects",
        slug="buildsphere",
        industry="Construction Project Management",
        size="201-500",
        currency="USD",
        timezone="America/Denver",
        exception_focus=("Procurement exceptions", "Vendor-payment exceptions", "Expense exceptions", "SLA compensation"),
    ),
    CompanyTemplate(
        name="PeopleGrid HR",
        slug="peoplegrid",
        industry="HR Technology",
        size="51-200",
        currency="GBP",
        timezone="Europe/London",
        exception_focus=("Enterprise discounts", "Setup-fee waivers", "Service credits", "Contract cancellation"),
    ),
    CompanyTemplate(
        name="ProcurePilot",
        slug="procurepilot",
        industry="Procurement Software",
        size="51-200",
        currency="USD",
        timezone="America/Los_Angeles",
        exception_focus=("Procurement exceptions", "Vendor-payment exceptions", "Enterprise discounts"),
    ),
    CompanyTemplate(
        name="StayRoute Business Travel",
        slug="stayroute",
        industry="Corporate Travel Management",
        size="201-500",
        currency="EUR",
        timezone="Europe/Berlin",
        exception_focus=("Expense exceptions", "Late refunds", "Service credits", "Vendor-payment exceptions"),
    ),
    CompanyTemplate(
        name="ServiceMint",
        slug="servicemint",
        industry="Field Service Platform",
        size="501-1000",
        currency="USD",
        timezone="America/New_York",
        exception_focus=("SLA compensation", "Service credits", "Implementation failures", "Operational exceptions"),
    ),
    CompanyTemplate(
        name="FinDesk Operations",
        slug="findesk",
        industry="Financial Operations Software",
        size="201-500",
        currency="USD",
        timezone="America/New_York",
        exception_focus=("Vendor-payment exceptions", "Expense exceptions", "Enterprise discounts", "SLA compensation"),
    ),
    CompanyTemplate(
        name="EventForge",
        slug="eventforge",
        industry="Enterprise Event Management",
        size="51-200",
        currency="USD",
        timezone="America/Los_Angeles",
        exception_focus=("Contract cancellation", "Service credits", "Setup-fee waivers", "Late refunds"),
    ),
    CompanyTemplate(
        name="DataBridge Analytics",
        slug="databridge",
        industry="Data and Analytics SaaS",
        size="201-500",
        currency="USD",
        timezone="America/Chicago",
        exception_focus=("Implementation failures", "Unsupported-feature promises", "Enterprise discounts", "SLA compensation"),
    ),
    # --- FULL_SYNTHETIC-only additions (3 extra companies) -----------------
    CompanyTemplate(
        name="HarvestLane Agritech",
        slug="harvestlane",
        industry="Agritech Supply Chain SaaS",
        size="51-200",
        currency="INR",
        timezone="Asia/Kolkata",
        exception_focus=("Late refunds", "Implementation failures", "Vendor-payment exceptions"),
    ),
    CompanyTemplate(
        name="Meridian Health Systems",
        slug="meridianhealth",
        industry="Healthcare Operations Software",
        size="501-1000",
        currency="USD",
        timezone="America/New_York",
        exception_focus=("SLA compensation", "Service credits", "Contract cancellation"),
    ),
    CompanyTemplate(
        name="OrbitalWorks Manufacturing",
        slug="orbitalworks",
        industry="Manufacturing ERP SaaS",
        size="1001-5000",
        currency="EUR",
        timezone="Europe/Berlin",
        exception_focus=("Procurement exceptions", "Vendor-payment exceptions", "Enterprise discounts"),
    ),
)


def companies_for_mode(mode: str) -> tuple[CompanyTemplate, ...]:
    if mode == MODE_FULL_SYNTHETIC:
        return COMPANY_TEMPLATES[:FULL_SYNTHETIC_COMPANY_COUNT]
    return COMPANY_TEMPLATES[:DEMO_SMALL_COMPANY_COUNT]


# ---------------------------------------------------------------------------
# Exception category taxonomy (shared across companies, code + name + sla)
# ---------------------------------------------------------------------------

EXCEPTION_CATEGORY_DEFS: tuple[dict, ...] = (
    {"code": "late_refund", "name": "Late Refunds", "default_sla_minutes": 4320},
    {"code": "enterprise_discount", "name": "Enterprise Discounts", "default_sla_minutes": 2880},
    {"code": "service_credit", "name": "Service Credits", "default_sla_minutes": 2880},
    {"code": "setup_fee_waiver", "name": "Setup-Fee Waivers", "default_sla_minutes": 1440},
    {"code": "contract_cancellation", "name": "Contract Cancellation", "default_sla_minutes": 5760},
    {"code": "implementation_failure", "name": "Implementation Failures", "default_sla_minutes": 2880},
    {"code": "unsupported_feature", "name": "Unsupported-Feature Promises", "default_sla_minutes": 4320},
    {"code": "sla_compensation", "name": "SLA Compensation", "default_sla_minutes": 1440},
    {"code": "vendor_payment", "name": "Vendor-Payment Exceptions", "default_sla_minutes": 2880},
    {"code": "expense_exception", "name": "Expense Exceptions", "default_sla_minutes": 1440},
    {"code": "procurement_exception", "name": "Procurement Exceptions", "default_sla_minutes": 2880},
    {"code": "operational_exception", "name": "Operational Exceptions", "default_sla_minutes": 1440},
)

# ---------------------------------------------------------------------------
# Status / urgency distributions for exception_cases
# ---------------------------------------------------------------------------

CASE_STATUS_WEIGHTS: tuple[tuple[str, int], ...] = (
    ("closed", 35),
    ("approved", 15),
    ("partially_approved", 12),
    ("denied", 10),
    ("escalated", 8),
    ("pending_decision", 8),
    ("analyzing", 6),
    ("submitted", 4),
    ("draft", 2),
)

URGENCY_WEIGHTS: tuple[tuple[str, int], ...] = (
    ("low", 25),
    ("medium", 45),
    ("high", 22),
    ("critical", 8),
)

# Roles used for fictional personas (kept out of `profiles` because that
# table FKs to auth.users; personas are embedded as JSON metadata instead).
PERSONA_ROLES: tuple[str, ...] = (
    "requester",
    "customer_success_manager",
    "sales_representative",
    "finance_manager",
    "policy_administrator",
    "department_head",
    "cfo",
    "auditor",
    "trainee",
)

SYNTHETIC_TAG = {"synthetic": True}
