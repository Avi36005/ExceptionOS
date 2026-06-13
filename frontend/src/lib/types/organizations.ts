import type { MemberRole, OrgStatus } from './common'

export interface Organization {
  id: string
  name: string
  slug: string
  industry?: string | null
  size?: string | null
  currency: string
  timezone: string
  status: OrgStatus
  hindsight_bank_id?: string | null
  created_at: string
  updated_at: string
  // UI-friendly extras some pages expect; optional until backend provides them
  plan?: string
  logo_url?: string | null
  hindsight_enabled?: boolean
  demo_mode?: boolean
}

export interface OrganizationCreate {
  name: string
  slug: string
  industry?: string | null
  size?: string | null
  currency?: string
  timezone?: string
}

export interface OrganizationUpdate {
  name?: string
  industry?: string | null
  size?: string | null
  currency?: string
  timezone?: string
  status?: OrgStatus
}

/** Row from `organization_memberships`, optionally joined with `organizations`. */
export interface OrganizationMembership {
  organization_id: string
  user_id: string
  role: MemberRole
  department_id?: string | null
  status: string
  joined_at?: string | null
  invited_by?: string | null
  organizations?: Organization
}

export interface Profile {
  id: string
  display_name?: string | null
  avatar_url?: string | null
  timezone?: string | null
  created_at?: string
}

export interface UserInvite {
  email: string
  role?: MemberRole
  department_id?: string | null
}

/** Member row from `/users/{organization_id}/members` (membership + profile). */
export interface OrganizationMember extends OrganizationMembership {
  profiles?: Profile
}
