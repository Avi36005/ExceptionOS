"""Map Hindsight memories to structured case evidence / precedent links."""
from __future__ import annotations

from typing import Any
from uuid import UUID


def map_memories_to_evidence(
    memories: list[dict[str, Any]],
    case_id: UUID,
) -> list[dict[str, Any]]:
    """Transform raw Hindsight recall results into structured evidence objects."""
    evidence = []
    for mem in memories:
        meta = mem.get("metadata", {})
        evidence.append(
            {
                "memory_id": mem.get("id"),
                "case_id": str(case_id),
                "content": mem.get("content", ""),
                "score": mem.get("score", 0.0),
                "memory_type": meta.get("type", "unknown"),
                "source_case_id": meta.get("case_id"),
                "decision_type": meta.get("decision_type"),
                "metadata": meta,
            }
        )
    return evidence


def map_memories_to_precedents(
    memories: list[dict[str, Any]],
    case_id: UUID,
) -> list[dict[str, Any]]:
    """Transform recall results into precedent_links rows."""
    precedents = []
    for mem in memories:
        meta = mem.get("metadata", {})
        source_case_id = meta.get("case_id")
        if not source_case_id:
            continue
        precedents.append(
            {
                "case_id": str(case_id),
                "precedent_case_id": source_case_id,
                "similarity_score": mem.get("score", 0.0),
                "similarity_reasons": [mem.get("content", "")[:200]],
                "difference_reasons": [],
                "memory_confidence": mem.get("score", 0.0),
                "relevance_adjustment": 0.0,
                "source_memory_ids": [mem.get("id", "")],
            }
        )
    return precedents
