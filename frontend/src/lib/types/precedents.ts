import type { HindsightMemory } from './exceptions'
import type { JsonObject } from './common'

export interface PrecedentSearchParams {
  q: string
  top_k?: number
}

export interface PrecedentSearchResult {
  results: HindsightMemory[]
  total: number
  query: string
  message?: string
}

export interface PrecedentLinkRow {
  id: string
  case_id: string
  precedent_case_id?: string | null
  memory_id?: string | null
  similarity_score?: number | null
  relationship_type?: string | null
  created_at?: string
  [key: string]: unknown
}

export interface PrecedentLinksParams {
  case_id?: string
}

// ---------------------------------------------------------------------------
// Precedent graph (extensible — backend agent may finalize node/edge shapes)
// ---------------------------------------------------------------------------

export type PrecedentGraphNodeType =
  | 'current_request'
  | 'historical_case'
  | 'policy'
  | 'root_cause'
  | 'decision'
  | 'outcome'
  | 'entity'

export type PrecedentGraphEdgeType =
  | 'similar_exception'
  | 'same_root_cause'
  | 'same_policy'
  | 'same_outcome'
  | 'contradictory_decision'
  | 'superseded_policy'
  | 'follow_up_outcome'

export interface PrecedentGraphNode {
  id: string
  type: PrecedentGraphNodeType
  label: string
  data?: JsonObject
  [key: string]: unknown
}

export interface PrecedentGraphEdge {
  id?: string
  source: string
  target: string
  type: PrecedentGraphEdgeType
  label?: string
  [key: string]: unknown
}

export interface PrecedentGraph {
  nodes: PrecedentGraphNode[]
  edges: PrecedentGraphEdge[]
  [key: string]: unknown
}

// ---------------------------------------------------------------------------
// "What would we usually do?" conversational ask
// ---------------------------------------------------------------------------

export interface PrecedentAskRequest {
  question: string
  case_id?: string
}

export interface PrecedentAskResponse {
  answer: string
  distribution_of_decisions?: JsonObject
  most_common_resolution?: string
  most_successful_resolution?: string
  supporting_cases?: JsonObject[]
  important_exceptions?: JsonObject[]
  hindsight_evidence?: HindsightMemory[]
  [key: string]: unknown
}

// ---------------------------------------------------------------------------
// Contradictions
// ---------------------------------------------------------------------------

export interface PrecedentContradiction {
  id?: string
  conflict_summary: string
  sources: JsonObject[]
  dates?: string[]
  reliability?: string
  suggested_authoritative_source?: string
  resolution_action?: string
  unresolved?: boolean
  [key: string]: unknown
}
