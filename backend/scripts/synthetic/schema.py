"""Shared schema metadata for the synthetic-data system.

Declares the FK-safe load order and per-table foreign-key relationships so the
validator (:mod:`validate_dataset`) and the loader (:mod:`seed_supabase`) agree
on one source of truth. Nothing here hits the network.
"""
from __future__ import annotations

# FK-safe insertion order. Parents precede children. ``synthetic_data_registry``
# is loaded last because it references every other synthetic row.
TABLE_LOAD_ORDER: tuple[str, ...] = (
    "organizations",
    "departments",
    "exception_categories",
    "policies",
    "policy_versions",
    "feature_flags",
    "sla_rules",
    "exception_cases",
    "case_facts",
    "case_evidence",
    "recommendations",
    "agent_runs",
    "agent_outputs",
    "case_events",
    "hindsight_operations",
    "exception_budgets",
    "budget_transactions",
    "benchmark_cohorts",
    "policy_drift_findings",
    "repeated_exception_clusters",
    "memory_contradictions",
    "training_scenarios",
    "openclaw_sessions",
    "voice_sessions",
    "synthetic_data_registry",
)

# Tables that must always be present in a non-empty dataset.
REQUIRED_TABLES: tuple[str, ...] = (
    "organizations",
    "departments",
    "exception_categories",
    "policies",
    "policy_versions",
    "exception_cases",
    "recommendations",
    "sla_rules",
    "exception_budgets",
    "budget_transactions",
    "synthetic_data_registry",
)

# Foreign keys to validate: table -> {column: referenced_table}. ``None``-valued
# cells are allowed (nullable FK). Self/cross references are resolved against the
# union of ids already collected for the referenced table.
FOREIGN_KEYS: dict[str, dict[str, str]] = {
    "departments": {"organization_id": "organizations"},
    "exception_categories": {"organization_id": "organizations"},
    "policies": {"organization_id": "organizations"},
    "policy_versions": {"policy_id": "policies"},
    "feature_flags": {"organization_id": "organizations"},
    "sla_rules": {"organization_id": "organizations", "category_id": "exception_categories"},
    "exception_cases": {
        "organization_id": "organizations",
        "category_id": "exception_categories",
        "department_id": "departments",
        "current_policy_version_id": "policy_versions",
    },
    "case_facts": {"case_id": "exception_cases"},
    "case_evidence": {"case_id": "exception_cases"},
    "recommendations": {"case_id": "exception_cases"},
    "agent_runs": {"case_id": "exception_cases"},
    "agent_outputs": {"agent_run_id": "agent_runs"},
    "case_events": {"case_id": "exception_cases", "organization_id": "organizations"},
    "hindsight_operations": {
        "organization_id": "organizations",
        "case_id": "exception_cases",
        "agent_run_id": "agent_runs",
    },
    "exception_budgets": {
        "organization_id": "organizations",
        "department_id": "departments",
        "category_id": "exception_categories",
    },
    "budget_transactions": {"budget_id": "exception_budgets", "case_id": "exception_cases"},
    "policy_drift_findings": {
        "organization_id": "organizations",
        "policy_id": "policies",
        "policy_version_id": "policy_versions",
    },
    "repeated_exception_clusters": {"organization_id": "organizations"},
    "memory_contradictions": {
        "organization_id": "organizations",
        "case_id_a": "exception_cases",
        "case_id_b": "exception_cases",
    },
    "training_scenarios": {"organization_id": "organizations", "source_case_id": "exception_cases"},
    "openclaw_sessions": {"organization_id": "organizations", "linked_case_id": "exception_cases"},
    "voice_sessions": {"organization_id": "organizations", "case_id": "exception_cases"},
    "benchmark_cohorts": {},
    "synthetic_data_registry": {"organization_id": "organizations"},
}

# Columns that reference exception_cases but are deferred during load to break
# the exception_cases <-> recommendations circular FK.
DEFERRED_CASE_COLUMNS: tuple[str, ...] = ("current_recommendation_id",)
