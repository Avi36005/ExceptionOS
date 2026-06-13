import type { JsonObject } from './common'
import type { Organization } from './organizations'

export interface AdminStats {
  total_organizations: number
  total_cases: number
  total_decisions: number
  total_agent_runs: number
  [key: string]: unknown
}

export interface AdminOrganizationsParams {
  page?: number
  page_size?: number
}

export interface AdminUsersParams {
  page?: number
  page_size?: number
}

export type AdminOrganizationList = Organization[]

/** System health — backend, providers, Hindsight, database, ElevenLabs, OpenClaw. */
export interface SystemHealthStatus {
  backend?: JsonObject
  providers?: JsonObject
  hindsight?: JsonObject
  database?: JsonObject
  elevenlabs?: JsonObject
  openclaw?: JsonObject
  [key: string]: unknown
}
