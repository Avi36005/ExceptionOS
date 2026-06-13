"""Stable Hindsight document ID builders.

Stable IDs let the same logical memory be re-retained (e.g. when a case is
re-analysed or an outcome is updated) without producing unbounded duplicate
memories, and let recall results be deduplicated/joined back to source rows.
"""
from __future__ import annotations

from uuid import UUID


def case_decision_document_id(organization_id: UUID | str, case_id: UUID | str, decision_id: UUID | str) -> str:
    return f"case:{organization_id}:{case_id}:decision:{decision_id}"


def case_outcome_document_id(organization_id: UUID | str, case_id: UUID | str) -> str:
    return f"case:{organization_id}:{case_id}:outcome"


def case_outcome_lesson_document_id(organization_id: UUID | str, case_id: UUID | str) -> str:
    return f"case:{organization_id}:{case_id}:outcome-lesson"

