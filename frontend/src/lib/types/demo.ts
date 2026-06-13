import type { JsonObject } from './common'

/**
 * Demo / replay endpoints — extensible placeholders since a companion
 * backend agent is still adding these routes (demo launcher, demo reset,
 * decision replay timeline, "what changed" recommendation diff).
 */

export interface DemoStatus {
  enabled: boolean
  organization_id?: string
  organization_slug?: string
  seeded?: boolean
  [key: string]: unknown
}

export interface DemoResetResponse {
  message: string
  organization_id?: string
  [key: string]: unknown
}

// ---------------------------------------------------------------------------
// Decision replay timeline (/app/exceptions/:caseId/replay)
// ---------------------------------------------------------------------------

export type ReplayEventType =
  | 'request_submitted'
  | 'policy_active'
  | 'hindsight_recall'
  | 'precedents_retrieved'
  | 'agent_debate'
  | 'recommendation'
  | 'human_override'
  | 'escalation'
  | 'final_decision'
  | 'outcome'
  | 'learned_observation'

export interface ReplayEvent {
  id?: string
  type: ReplayEventType | string
  ts: string
  title?: string
  summary?: string
  data?: JsonObject
  [key: string]: unknown
}

export interface ReplayTimeline {
  case_id: string
  events: ReplayEvent[]
  [key: string]: unknown
}

// ---------------------------------------------------------------------------
// "What changed" recommendation version comparison
// (/app/exceptions/:caseId/what-changed)
// ---------------------------------------------------------------------------

export interface WhatChangedResponse {
  previous_recommendation?: JsonObject
  current_recommendation?: JsonObject
  new_facts?: JsonObject[]
  new_memories?: JsonObject[]
  new_policy?: JsonObject
  new_evidence?: JsonObject[]
  changed_confidence?: { previous?: number; current?: number }
  provider_fallback?: JsonObject
  [key: string]: unknown
}

// ---------------------------------------------------------------------------
// Exceptions "answer-question" (Missing Information Agent follow-up)
// ---------------------------------------------------------------------------

export interface AnswerQuestionResponse {
  updated_facts?: JsonObject[]
  recommendation_readiness?: number
  what_changed?: JsonObject
  triggered_recall?: boolean
  [key: string]: unknown
}
