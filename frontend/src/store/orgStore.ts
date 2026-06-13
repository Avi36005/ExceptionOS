import { create } from 'zustand'

export interface Organization {
  id: string
  name: string
  slug: string
  plan: string
  logoUrl?: string
  hindsightEnabled: boolean
  demoMode: boolean
}

export interface OrgMembership {
  orgId: string
  orgName: string
  orgSlug: string
  role: 'owner' | 'admin' | 'manager' | 'approver' | 'submitter' | 'viewer'
  department?: string
}

interface OrgState {
  currentOrg: Organization | null
  memberships: OrgMembership[]
  userRole: string | null
  setCurrentOrg: (org: Organization | null) => void
  setMemberships: (memberships: OrgMembership[]) => void
  setUserRole: (role: string | null) => void
  isAdmin: () => boolean
  isManager: () => boolean
}

export const useOrgStore = create<OrgState>((set, get) => ({
  currentOrg: null,
  memberships: [],
  userRole: null,

  setCurrentOrg: (org) => set({ currentOrg: org }),
  setMemberships: (memberships) => set({ memberships }),
  setUserRole: (role) => set({ userRole: role }),

  isAdmin: () => {
    const role = get().userRole
    return role === 'owner' || role === 'admin'
  },

  isManager: () => {
    const role = get().userRole
    return role === 'owner' || role === 'admin' || role === 'manager'
  },
}))
