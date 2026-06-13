import type { Urgency } from './common'

export interface TrainingScenario {
  id: string
  scenario_number: number
  difficulty: 'easy' | 'medium' | 'hard'
  expected_outcome: string
  title: string
  description: string
  entity_name?: string | null
  requested_amount?: number | null
  urgency: Urgency
  category?: string
  [key: string]: unknown
}

export interface TrainingScenarioRunResult {
  case_id: string
  scenario: TrainingScenario
  message: string
  [key: string]: unknown
}

/** Placeholder for /training/history — extensible until backend finalizes. */
export interface TrainingHistoryEntry {
  id?: string
  scenario_id?: string
  case_id?: string
  score?: number
  completed_at?: string
  [key: string]: unknown
}
