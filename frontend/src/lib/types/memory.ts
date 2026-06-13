import type { JsonObject } from './common'
import type { HindsightMemory } from './exceptions'

export interface RetainRequest {
  content: string
  metadata?: JsonObject
  case_id?: string
}

export interface RecallRequest {
  query: string
  top_k?: number
  case_id?: string
}

export interface ReflectRequest {
  topic: string
  case_id?: string
}

export interface RecallResponse {
  memories: HindsightMemory[]
  total: number
}

export interface ReflectResponse {
  [key: string]: unknown
}

// ---------------------------------------------------------------------------
// Hindsight Activity Panel — operation log taxonomy
//
// Mirrors the SSE event taxonomy emitted by the orchestrator AND (likely) a
// REST endpoint backed by `operation_logger` for historical activity.
// Kept generic since the backend agent's `OperationLogContext` schema may
// gain fields.
// ---------------------------------------------------------------------------

export type HindsightOperationType =
  | 'BANK_SELECTED'
  | 'RETAIN_STARTED'
  | 'RETAIN_COMPLETED'
  | 'RECALL_STARTED'
  | 'RECALL_COMPLETED'
  | 'REFLECT_STARTED'
  | 'REFLECT_COMPLETED'
  | 'MEMORY_EXPANDED'
  | 'MEMORY_LINKED'
  | 'OBSERVATION_USED'
  | 'MENTAL_MODEL_USED'
  | 'OPERATION_FAILED'
  | 'MEMORY_USED'
  | 'PROVIDER_FALLBACK'

export interface HindsightOperationEvent {
  operation: HindsightOperationType | string
  timestamp?: string
  bank_id?: string
  case_id?: string
  query_summary?: string
  document_id?: string
  memories_returned?: number
  source_memory_ids?: string[]
  duration_ms?: number
  token_usage?: JsonObject
  provider?: string
  status?: string
  error?: string
  [key: string]: unknown
}

/** Evidence drawer contents for a recommendation's "View Hindsight Evidence". */
export interface HindsightEvidence {
  policy_memories?: HindsightMemory[]
  precedent_memories?: HindsightMemory[]
  outcome_memories?: HindsightMemory[]
  [key: string]: unknown
}
