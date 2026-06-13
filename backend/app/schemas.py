"""Shared Pydantic v2 schemas used across the application."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class OrgStatus(str, Enum):
    active = "active"
    suspended = "suspended"
    trial = "trial"


class MemberRole(str, Enum):
    owner = "owner"
    admin = "admin"
    manager = "manager"
    analyst = "analyst"
    viewer = "viewer"


class ExceptionStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"
    intake = "intake"
    analyzing = "analyzing"
    pending_decision = "pending_decision"
    approved = "approved"
    partially_approved = "partially_approved"
    denied = "denied"
    escalated = "escalated"
    closed = "closed"


class Urgency(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class PolicyStatus(str, Enum):
    draft = "draft"
    active = "active"
    archived = "archived"


class DecisionType(str, Enum):
    approved = "approved"
    partially_approved = "partially_approved"
    denied = "denied"
    escalated = "escalated"


class RecommendationType(str, Enum):
    approve = "approve"
    partially_approve = "partially_approve"
    deny = "deny"
    escalate = "escalate"
    needs_more_info = "needs_more_info"


class AgentRunStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


# ---------------------------------------------------------------------------
# Common response wrappers
# ---------------------------------------------------------------------------

class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    pages: int


class DataResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    data: Any
    meta: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    code: str | None = None


class MessageResponse(BaseModel):
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Organisation schemas
# ---------------------------------------------------------------------------

class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    slug: str = Field(..., min_length=2, max_length=80, pattern=r"^[a-z0-9-]+$")
    industry: str | None = None
    size: str | None = None
    currency: str = "USD"
    timezone: str = "UTC"


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = None
    industry: str | None = None
    size: str | None = None
    currency: str | None = None
    timezone: str | None = None
    status: OrgStatus | None = None


class OrganizationRead(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: OrgStatus
    hindsight_bank_id: str | None = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# User / profile schemas
# ---------------------------------------------------------------------------

class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    display_name: str | None = None
    avatar_url: str | None = None
    timezone: str | None = None
    created_at: datetime


class MembershipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    organization_id: UUID
    user_id: UUID
    role: MemberRole
    department_id: UUID | None = None
    status: str
    joined_at: datetime | None = None


class UserInvite(BaseModel):
    email: str
    role: MemberRole = MemberRole.analyst
    department_id: UUID | None = None


# ---------------------------------------------------------------------------
# Exception case schemas
# ---------------------------------------------------------------------------

class ExceptionCaseBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    description: str | None = None
    entity_name: str | None = None
    requested_amount: float | None = None
    currency: str = "USD"
    annual_value: float | None = None
    request_date: datetime | None = None
    transaction_date: datetime | None = None
    root_cause: str | None = None
    urgency: Urgency = Urgency.medium
    category_id: UUID | None = None
    department_id: UUID | None = None


class ExceptionCaseCreate(ExceptionCaseBase):
    pass


class ExceptionCaseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    entity_name: str | None = None
    requested_amount: float | None = None
    urgency: Urgency | None = None
    status: ExceptionStatus | None = None
    assignee_user_id: UUID | None = None


class ExceptionCaseRead(ExceptionCaseBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    case_number: str
    status: ExceptionStatus
    requester_user_id: UUID | None = None
    assignee_user_id: UUID | None = None
    sla_due_at: datetime | None = None
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    version: int = 1


# ---------------------------------------------------------------------------
# Policy schemas
# ---------------------------------------------------------------------------

class PolicyBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=300)
    category: str | None = None


class PolicyCreate(PolicyBase):
    content: str
    effective_from: datetime | None = None


class PolicyUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    status: PolicyStatus | None = None


class PolicyVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    policy_id: UUID
    version_label: str
    content: str
    effective_from: datetime | None = None
    effective_to: datetime | None = None
    status: PolicyStatus
    created_at: datetime


class PolicyRead(PolicyBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    status: PolicyStatus
    owner_user_id: UUID | None = None
    versions: list[PolicyVersionRead] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Recommendation schemas
# ---------------------------------------------------------------------------

class RiskInfo(BaseModel):
    level: str = "medium"
    factors: list[str] = Field(default_factory=list)
    score: float | None = None


class RecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    case_id: UUID
    version: int
    recommendation_type: RecommendationType
    recommended_amount: float | None = None
    conditions: list[str] = Field(default_factory=list)
    confidence: float
    reasoning: str
    risk: RiskInfo = Field(default_factory=RiskInfo)
    provider_summary: dict[str, Any] = Field(default_factory=dict)
    hindsight_evidence: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime


# ---------------------------------------------------------------------------
# Decision schemas
# ---------------------------------------------------------------------------

class DecisionCreate(BaseModel):
    decision_type: DecisionType
    approved_amount: float | None = None
    conditions: list[str] = Field(default_factory=list)
    reasoning: str
    override: bool = False


class DecisionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    case_id: UUID
    recommendation_id: UUID | None = None
    decision_type: DecisionType
    approved_amount: float | None = None
    conditions: list[str] = Field(default_factory=list)
    reasoning: str
    override: bool
    decided_by: UUID
    decided_at: datetime


# ---------------------------------------------------------------------------
# Outcome schemas
# ---------------------------------------------------------------------------

class OutcomeCreate(BaseModel):
    actual_outcome: str
    outcome_date: datetime | None = None
    financial_impact: float | None = None
    notes: str | None = None


class OutcomeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    case_id: UUID
    decision_id: UUID | None = None
    actual_outcome: str
    outcome_date: datetime | None = None
    financial_impact: float | None = None
    notes: str | None = None
    recorded_by: UUID
    created_at: datetime


# ---------------------------------------------------------------------------
# Memory schemas
# ---------------------------------------------------------------------------

class RetainRequest(BaseModel):
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    case_id: UUID | None = None


class RecallRequest(BaseModel):
    query: str
    top_k: int = Field(default=10, ge=1, le=50)
    case_id: UUID | None = None


class ReflectRequest(BaseModel):
    topic: str
    case_id: UUID | None = None


# ---------------------------------------------------------------------------
# Debate / analysis schemas
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    force_rerun: bool = False
    demo_mode: bool = False


class DebateEvent(BaseModel):
    event: str
    agent: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Insight schemas
# ---------------------------------------------------------------------------

class DashboardMetrics(BaseModel):
    total_cases: int
    open_cases: int
    pending_decision: int
    resolved_this_month: int
    approval_rate: float
    average_resolution_hours: float
    policy_drift_alerts: int


class PolicyDriftAlert(BaseModel):
    policy_id: UUID
    policy_name: str
    drift_score: float
    description: str
    detected_at: datetime


class RepeatedExceptionPattern(BaseModel):
    pattern: str
    occurrences: int
    category: str | None
    average_amount: float | None
    recommendation_consistency: float


# ---------------------------------------------------------------------------
# Agent run schemas
# ---------------------------------------------------------------------------

class AgentRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    case_id: UUID
    run_type: str
    status: AgentRunStatus
    started_at: datetime
    completed_at: datetime | None = None
    trace_id: str | None = None
    final_provider: str | None = None
    fallback_path: list[str] = Field(default_factory=list)
    latency_ms: int | None = None
    token_usage: dict[str, Any] = Field(default_factory=dict)
    error: dict[str, Any] | None = None
