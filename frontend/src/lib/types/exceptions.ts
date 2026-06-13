import type { ExceptionStatus, JsonObject, RecommendationType, Urgency } from './common'

export interface ExceptionCase {
  id: string
  organization_id: string
  case_number: string
  title: string
  description?: string | null
  entity_name?: string | null
  requested_amount?: number | null
  currency: string
  annual_value?: number | null
  request_date?: string | null
  transaction_date?: string | null
  root_cause?: string | null
  urgency: Urgency
  category_id?: string | null
  department_id?: string | null
  status: ExceptionStatus
  requester_user_id?: string | null
  assignee_user_id?: string | null
  sla_due_at?: string | null
  resolved_at?: string | null
  created_at: string
  updated_at: string
  version: number
  current_recommendation_id?: string | null
  // Allow additional fields the backend may add without breaking types
  [key: string]: unknown
}

export interface ExceptionCaseCreate {
  title: string
  description?: string
  entity_name?: string
  requested_amount?: number
  currency?: string
  annual_value?: number
  request_date?: string
  transaction_date?: string
  root_cause?: string
  urgency?: Urgency
  category_id?: string
  department_id?: string
  // Conversational intake / additional context fields
  customer_vendor_employee_entity?: string
  business_impact?: string
  known_policy?: string
  requested_resolution?: string
  commercial_value?: number
  risk_of_rejection?: string
  additional_context?: string
  [key: string]: unknown
}

export interface ExceptionCaseUpdate {
  title?: string
  description?: string
  entity_name?: string
  requested_amount?: number
  urgency?: Urgency
  status?: ExceptionStatus
  assignee_user_id?: string
  [key: string]: unknown
}

export interface ExceptionListParams {
  page?: number
  page_size?: number
  status?: ExceptionStatus | string
}

// ---------------------------------------------------------------------------
// Recommendation
// ---------------------------------------------------------------------------

export interface RiskInfo {
  level: string
  factors: string[]
  score?: number | null
}

export interface Recommendation {
  id: string
  case_id: string
  version: number
  recommendation_type: RecommendationType
  recommended_amount?: number | null
  conditions: string[]
  confidence: number
  reasoning: string
  risk: RiskInfo
  provider_summary: JsonObject
  hindsight_evidence: JsonObject[]
  created_at: string
  [key: string]: unknown
}

// ---------------------------------------------------------------------------
// Decisions & Outcomes
// ---------------------------------------------------------------------------

export interface DecisionCreate {
  decision_type: string
  approved_amount?: number | null
  conditions?: string[]
  reasoning: string
  override?: boolean
  [key: string]: unknown
}

export interface Decision {
  id: string
  case_id: string
  recommendation_id?: string | null
  decision_type: string
  approved_amount?: number | null
  conditions: string[]
  reasoning: string
  override: boolean
  decided_by: string
  decided_at: string
  [key: string]: unknown
}

export interface OutcomeCreate {
  actual_outcome: string
  outcome_date?: string
  financial_impact?: number
  notes?: string
  [key: string]: unknown
}

export interface Outcome {
  id: string
  case_id: string
  decision_id?: string | null
  actual_outcome: string
  outcome_date?: string | null
  financial_impact?: number | null
  notes?: string | null
  recorded_by: string
  created_at: string
  [key: string]: unknown
}

// ---------------------------------------------------------------------------
// Precedent links / memory
// ---------------------------------------------------------------------------

export interface PrecedentLink {
  id: string
  case_id: string
  precedent_case_id?: string | null
  memory_id?: string | null
  similarity_score?: number | null
  relationship_type?: string | null
  [key: string]: unknown
}

export interface HindsightMemory {
  id?: string
  score?: number
  content?: string
  metadata?: JsonObject
  [key: string]: unknown
}

export interface CaseMemoryResponse {
  memories: HindsightMemory[]
  bank_id?: string
  message?: string
}

// ---------------------------------------------------------------------------
// Audit
// ---------------------------------------------------------------------------

export interface AuditEvent {
  id?: string
  case_id: string
  organization_id?: string
  event_type: string
  actor_type?: string
  actor_id?: string
  payload?: JsonObject
  created_at?: string
  [key: string]: unknown
}

// ---------------------------------------------------------------------------
// Intake / Analysis
// ---------------------------------------------------------------------------

export interface AnalyzeRequest {
  force_rerun?: boolean
  demo_mode?: boolean
}

export interface IntakeResult {
  output: {
    key_facts?: JsonObject[]
    urgency?: Urgency
    missing_fields?: string[]
    recommended_fields?: string[]
    confidence?: number
    [key: string]: unknown
  }
  [key: string]: unknown
}

// ---------------------------------------------------------------------------
// "Answer question" (Missing Information Agent) — extensible placeholder
// ---------------------------------------------------------------------------

export interface ExceptionQuestion {
  id: string
  case_id: string
  question: string
  field?: string | null
  why_it_matters?: string | null
  required?: boolean
  answered?: boolean
  answer?: string | null
  [key: string]: unknown
}

export interface AnswerQuestionRequest {
  question_id?: string
  field?: string
  answer: string
  [key: string]: unknown
}
