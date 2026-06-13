from __future__ import annotations
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class AgentRunRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    case_id: UUID
    run_type: str
    status: str = "pending"
    started_at: datetime
    completed_at: datetime | None = None
    trace_id: str | None = None
    final_provider: str | None = None
    fallback_path_json: str = "[]"
    latency_ms: int | None = None
    token_usage_json: str = "{}"
    error_json: str | None = None


class AgentOutputRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    agent_run_id: UUID
    agent_name: str
    provider: str | None = None
    model: str | None = None
    status: str
    structured_output_json: str = "{}"
    latency_ms: int | None = None
    token_usage_json: str = "{}"
    created_at: datetime
