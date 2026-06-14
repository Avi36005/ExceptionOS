import { useNavigate } from 'react-router-dom'
import { Building2, Plus, Zap, ArrowRight } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { useOrgStore } from '../../store/orgStore'

const mockOrgs = [
  { id: '0', name: 'NovaFlow Systems', slug: 'novaflow', plan: 'enterprise', role: 'admin', memberCount: 64 },
  { id: '1', name: 'Acme Corporation', slug: 'acme', plan: 'enterprise', role: 'admin', memberCount: 42 },
  { id: '2', name: 'TechStartup Inc.', slug: 'techstartup', plan: 'growth', role: 'manager', memberCount: 12 },
  { id: '3', name: 'Global Finance Inc.', slug: 'global-finance', plan: 'enterprise', role: 'reviewer', memberCount: 128 },
  { id: '4', name: 'Northwind Health', slug: 'northwind-health', plan: 'enterprise', role: 'admin', memberCount: 76 },
  { id: '5', name: 'BlueOcean Logistics', slug: 'blueocean', plan: 'growth', role: 'manager', memberCount: 31 },
  { id: '6', name: 'Vertex Legal Group', slug: 'vertex-legal', plan: 'business', role: 'reviewer', memberCount: 18 },
  { id: '7', name: 'Sunrise Retail Co.', slug: 'sunrise-retail', plan: 'starter', role: 'admin', memberCount: 9 },
  { id: '8', name: 'ExceptionOS QA Demo', slug: 'exceptionos-qa-demo', plan: 'enterprise', role: 'admin', memberCount: 5 },
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
    <div className="min-h-screen bg-light flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        <div className="flex items-center justify-center gap-2 mb-10">
          <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-gray-900">ExceptionOS</span>
        </div>

        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Choose an organization</h1>
          <p className="text-gray-500">Welcome back, {user?.user_metadata?.full_name?.split(' ')[0] || 'there'}! Select an organization to continue.</p>
        </div>

        <div className="space-y-3 mb-6">
          {mockOrgs.map(org => (
            <button
              key={org.id}
              onClick={() => selectOrg(org)}
              className="w-full flex items-center gap-4 p-4 bg-white rounded-xl border border-gray-200 hover:border-primary/30 hover:bg-gray-50 transition-all text-left group"
            >
              <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center shrink-0">
                <Building2 className="w-6 h-6 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold text-gray-900">{org.name}</div>
                <div className="text-xs text-gray-500 mt-0.5">{org.memberCount} members · {org.plan} plan · {org.role}</div>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-600 group-hover:text-primary transition-colors shrink-0" />
            </button>
          ))}
        </div>

        <button
          onClick={() => navigate('/onboarding/company')}
          className="w-full flex items-center justify-center gap-2 p-4 border-2 border-dashed border-gray-200 rounded-xl text-gray-500 hover:text-gray-900 hover:border-primary/30 transition-all text-sm font-medium"
        >
          <Plus className="w-4 h-4" />
          Create new organization
        </button>
      </div>
    </div>
  )
}
