import type { PolicyStatus } from './common'

export interface PolicyVersion {
  id: string
  policy_id: string
  version_label: string
  content: string
  effective_from?: string | null
  effective_to?: string | null
  status: PolicyStatus
  created_at: string
  [key: string]: unknown
}

export interface Policy {
  id: string
  organization_id: string
  name: string
  category?: string | null
  status: PolicyStatus
  owner_user_id?: string | null
  versions: PolicyVersion[]
  [key: string]: unknown
}

export interface PolicyCreate {
  name: string
  category?: string
  content: string
  effective_from?: string
}

export interface PolicyUpdate {
  name?: string
  category?: string
  status?: PolicyStatus
}

export interface PolicyListParams {
  page?: number
  page_size?: number
}
