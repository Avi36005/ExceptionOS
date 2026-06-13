import { useNavigate } from 'react-router-dom'
import { Building2, Plus, Zap, ArrowRight } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { useOrgStore } from '../../store/orgStore'

const mockOrgs = [
  { id: '1', name: 'Acme Corporation', slug: 'acme', plan: 'enterprise', role: 'admin', memberCount: 42 },
  { id: '2', name: 'TechStartup Inc.', slug: 'techstartup', plan: 'growth', role: 'manager', memberCount: 12 },
]

export default function SelectOrg() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { setCurrentOrg, setUserRole } = useOrgStore()

  const selectOrg = (org: typeof mockOrgs[0]) => {
    setCurrentOrg({
      id: org.id,
      name: org.name,
      slug: org.slug,
      plan: org.plan,
      hindsightEnabled: true,
      demoMode: false,
    })
    setUserRole(org.role)
    navigate('/app')
  }

  return (
    <div className="min-h-screen bg-dark flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        <div className="flex items-center justify-center gap-2 mb-10">
          <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-white">ExceptionOS</span>
        </div>

        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-white mb-2">Choose an organization</h1>
          <p className="text-gray-400">Welcome back, {user?.user_metadata?.full_name?.split(' ')[0] || 'there'}! Select an organization to continue.</p>
        </div>

        <div className="space-y-3 mb-6">
          {mockOrgs.map(org => (
            <button
              key={org.id}
              onClick={() => selectOrg(org)}
              className="w-full flex items-center gap-4 p-4 bg-dark2 rounded-xl border border-white/10 hover:border-primary/30 hover:bg-white/5 transition-all text-left group"
            >
              <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center shrink-0">
                <Building2 className="w-6 h-6 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold text-white">{org.name}</div>
                <div className="text-xs text-gray-500 mt-0.5">{org.memberCount} members · {org.plan} plan · {org.role}</div>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-600 group-hover:text-primary transition-colors shrink-0" />
            </button>
          ))}
        </div>

        <button
          onClick={() => navigate('/onboarding/company')}
          className="w-full flex items-center justify-center gap-2 p-4 border-2 border-dashed border-white/10 rounded-xl text-gray-400 hover:text-white hover:border-primary/30 transition-all text-sm font-medium"
        >
          <Plus className="w-4 h-4" />
          Create new organization
        </button>
      </div>
    </div>
  )
}
