import type { JsonObject } from './common'

/**
 * SSE event taxonomy emitted by `backend/app/agents/orchestrator.py` via
 * `Orchestrator.run_stream`. Each chunk is `data: {"event": ..., "data": ...,
 * "ts": ...}\n\n`.
 *
 * `NEEDS_INFO` is listed as a possible future addition by the backend agent
 * (Missing Information Agent) — included here so the frontend doesn't break
 * when it appears.
 */
export type DebateEventName =
  | 'start'
  | 'status'
  | 'agent_start'
  | 'agent_done'
  | 'agent_error'
  | 'debate_start'
  | 'RECALL_STARTED'
  | 'RECALL_COMPLETED'
  | 'MEMORY_USED'
  | 'RETAIN_STARTED'
  | 'RETAIN_COMPLETED'
  | 'REFLECT_STARTED'
  | 'REFLECT_COMPLETED'
  | 'PROVIDER_FALLBACK'
  | 'OPERATION_FAILED'
  | 'NEEDS_INFO'
  | 'complete'
  | 'error'

export interface DebateEvent<T = JsonObject> {
  event: DebateEventName | string
  data: T
  ts: string
}

// ---------------------------------------------------------------------------
// Known per-event `data` shapes (best-effort; all fields optional since the
// backend agent may still be iterating on exact payloads)
// ---------------------------------------------------------------------------

export interface StartEventData {
  trace_id: string
  case_id: string
  agent_run_id: string
}

export interface StatusEventData {
  status: string
  case_id: string
}

export type AgentName =
  | 'intake_agent'
  | 'policy_agent'
  | 'precedent_agent'
  | 'finance_agent'
  | 'customer_impact_agent'
  | 'risk_agent'
  | 'counter_precedent_agent'
  | 'consistency_agent'
  | 'critic_agent'
  | 'final_decision_agent'
  | string

export interface AgentStartEventData {
  agent: AgentName
}

export interface AgentDoneEventData {
  agent: AgentName
  output: JsonObject
}

export interface AgentErrorEventData {
  agent: AgentName
  error: string
}

export interface DebateStartEventData {
  agents: string[]
}

export interface MemoryUsedEventData {
  memories: Array<{
    memory_id?: string
    score?: number
    type?: string
    document_id?: string
    snippet?: string
    [key: string]: unknown
  }>
}

export interface RecallCompletedEventData {
  counts: Record<string, number>
}

export interface RetainEventData {
  document_id: string
  bank_id?: string
}

export interface ProviderFallbackEventData {
  agent: string
  failed_providers: string[]
  final_provider?: string
}

export interface OperationFailedEventData {
  operation: string
  error: string
  document_id?: string
  [key: string]: unknown
}

export interface CompleteEventData {
  recommendation_id: string
  recommendation_type: string
  confidence: number
  latency_ms: number
  token_usage: JsonObject
}

export interface ErrorEventData {
  message: string
  case_id?: string
}

export interface NeedsInfoEventData {
  questions?: Array<{
    id?: string
    question: string
    field?: string
    why_it_matters?: string
    [key: string]: unknown
  }>
  [key: string]: unknown
}

// ---------------------------------------------------------------------------
// Reactive state shapes for useDebateStream
// ---------------------------------------------------------------------------

export type AgentStatus = 'pending' | 'running' | 'done' | 'error'

export interface AgentState {
  agent: AgentName
  status: AgentStatus
  output?: JsonObject
  error?: string
  startedAt?: string
  doneAt?: string
}

export interface MemoryActivityEntry {
  id: string
  event: DebateEventName | string
  data: JsonObject
  ts: string
}

export interface DebateStreamState {
  /** Raw connection lifecycle */
  connectionStatus: 'idle' | 'connecting' | 'open' | 'closed' | 'error'
  /** Latest top-level status (e.g. "analyzing") */
  status: string | null
  traceId: string | null
  agentRunId: string | null
  /** Per-agent state, in pipeline order as agents start */
  agents: AgentState[]
  /** Chronological list of Hindsight memory/recall/retain/fallback/failure events
   *  — feeds the Hindsight Activity Panel */
  memoryActivity: MemoryActivityEntry[]
  /** Provider fallback notices */
  fallbacks: ProviderFallbackEventData[]
  /** Operation failures (recall/retain/etc.) */
  failures: OperationFailedEventData[]
  /** Any NEEDS_INFO payloads received */
  needsInfo: NeedsInfoEventData[]
  /** Final result, if completed */
  complete: CompleteEventData | null
  /** Error message, if the stream errored */
  error: string | null
  /** All raw events received, in order (for debugging / replay) */
  events: DebateEvent[]
}
