import type { JsonObject } from './common'

export interface DashboardMetrics {
  total_cases: number
  open_cases: number
  pending_decision: number
  resolved_this_month: number
  approval_rate: number
  average_resolution_hours: number
  policy_drift_alerts: number
  // Extra fields the spec calls for on /app dashboard; optional until backend
  // agent adds them to the response.
  exceptions_awaiting_action?: number
  exceptions_approaching_sla?: number
  total_financial_exposure?: number
  exception_budget_remaining?: number
  decision_consistency_score?: number
  hindsight_memories_added_this_week?: number
  hindsight_recalls_this_week?: number
  outcome_completion_rate?: number
  [key: string]: unknown
}

export interface PolicyDriftFinding {
  policy_id?: string
  policy_name?: string
  drift_score?: number
  description?: string
  detected_at?: string
  [key: string]: unknown
}

export interface RepeatedExceptionPattern {
  pattern: string
  occurrences: number
  entity_name?: string | null
  category?: string | null
  average_amount?: number | null
  statuses?: string[]
  recommendation_consistency?: number
  [key: string]: unknown
}

/** Generic shape for the remaining /insights/* endpoints (root-causes,
 * consistency, outcomes, success, budgets, benchmarks, memory-health,
 * provider-usage) — kept loose pending final backend response shapes. */
export type InsightsGenericResponse = JsonObject
