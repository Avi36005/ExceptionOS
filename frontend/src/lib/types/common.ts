/**
 * Shared response envelopes and primitive types matching the backend's
 * `app.schemas` Pydantic models (DataResponse, PaginationMeta, etc).
 *
 * Keep these generic/loose where the backend agent's exact final shape is
 * still in flux — prefer optional fields and index signatures so the
 * frontend doesn't break when new fields are added.
 */

export interface PaginationMeta {
  total: number
  page: number
  page_size: number
  pages: number
}

/** Generic API envelope: `{ data: T, meta?: {...} }` */
export interface DataResponse<T> {
  data: T
  meta?: PaginationMeta | Record<string, unknown>
}

export interface MessageResponse<T = Record<string, unknown>> {
  message: string
  data?: T
}

export interface ApiErrorBody {
  error?: string
  detail?: string | Record<string, unknown> | Array<Record<string, unknown>>
  code?: string
}

/** Normalized error thrown by the API client for all non-2xx responses. */
export class ApiError extends Error {
  status: number
  body: ApiErrorBody | null
  url: string

  constructor(message: string, status: number, body: ApiErrorBody | null, url: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.body = body
    this.url = url
  }
}

// ---------------------------------------------------------------------------
// Enums (mirrors app/schemas.py)
// ---------------------------------------------------------------------------

export type OrgStatus = 'active' | 'suspended' | 'trial'

export type MemberRole = 'owner' | 'admin' | 'manager' | 'analyst' | 'viewer'

export type ExceptionStatus =
  | 'draft'
  | 'submitted'
  | 'intake'
  | 'collecting_information'
  | 'ready_for_analysis'
  | 'analyzing'
  | 'recommendation_ready'
  | 'pending_decision'
  | 'awaiting_approval'
  | 'escalated'
  | 'approved'
  | 'partially_approved'
  | 'denied'
  | 'rejected'
  | 'withdrawn'
  | 'outcome_pending'
  | 'resolved'
  | 'closed'
  | 'archived'

export type Urgency = 'low' | 'medium' | 'high' | 'critical'

export type PolicyStatus = 'draft' | 'active' | 'archived'

export type DecisionType =
  | 'approved'
  | 'partially_approved'
  | 'denied'
  | 'escalated'
  | 'rejected'
  | 'withdrawn'
  | 'deferred'
  | 'modified'
  | 'request_information'

export type RecommendationType =
  | 'approve'
  | 'partially_approve'
  | 'deny'
  | 'escalate'
  | 'needs_more_info'

export type AgentRunStatus = 'pending' | 'running' | 'completed' | 'failed'

// ---------------------------------------------------------------------------
// Generic helpers
// ---------------------------------------------------------------------------

/** Loosely-typed JSON object for fields whose exact shape is still evolving. */
export type JsonObject = Record<string, unknown>

export interface ListParams {
  page?: number
  page_size?: number
  [key: string]: unknown
}
