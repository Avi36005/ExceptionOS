import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Edit, BookOpen, Clock, User, Tag, TrendingUp, Shield } from 'lucide-react'

export default function PolicyDetail() {
  const { policyId } = useParams()
  const navigate = useNavigate()

  return (
    <div className="fade-in max-w-4xl">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate('/app/policies')} className="p-2 rounded-lg hover:bg-gray-50 text-gray-500 hover:text-gray-900 transition-colors">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono text-primary">{policyId}</span>
            <span className="px-2 py-0.5 rounded-md text-xs bg-green-50 text-green-700 ring-1 ring-green-600/20 font-medium">Active</span>
            <span className="text-xs text-gray-500">v2.3</span>
          </div>
          <h1 className="text-xl font-bold text-gray-900">IT Software Procurement Policy</h1>
        </div>
        <div className="flex gap-2">
          <button onClick={() => navigate(`/app/policies/${policyId}/versions`)} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-100 hover:bg-gray-100 text-gray-900 text-sm font-medium border border-gray-200 transition-colors">
            <Clock className="w-4 h-4" /> History
          </button>
          <button onClick={() => navigate(`/app/policies/${policyId}/edit`)} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-sm font-medium transition-colors">
            <Edit className="w-4 h-4" /> Edit
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="prose prose-sm max-w-none">
              <h2 className="text-base font-semibold text-gray-900 mt-0">Purpose</h2>
              <p className="text-gray-600 text-sm leading-relaxed">This policy establishes guidelines for the procurement of software tools and licenses across all departments, ensuring security compliance, budget controls, and vendor due diligence.</p>

              <h2 className="text-base font-semibold text-gray-900">Scope</h2>
              <p className="text-gray-600 text-sm leading-relaxed">This policy applies to all employees, contractors, and vendors who request or procure software on behalf of the organization.</p>

              <h2 className="text-base font-semibold text-gray-900">Policy Statement</h2>
              <p className="text-gray-600 text-sm leading-relaxed">All software purchases exceeding $1,000 annually must undergo a 30-day procurement review process, including:</p>
              <ul className="text-gray-600 text-sm space-y-1 mt-2">
                <li>Security vetting by the CISO office</li>
                <li>Budget authorization from department head</li>
                <li>Vendor risk assessment</li>
                <li>Legal review of license terms for enterprise software</li>
              </ul>

              <h2 className="text-base font-semibold text-gray-900">Emergency Exceptions</h2>
              <p className="text-gray-600 text-sm leading-relaxed">In time-critical situations, the 30-day requirement may be waived with VP-level approval and CISO expedited review (24-hour turnaround). All emergency exceptions must be submitted through ExceptionOS and documented with business impact justification.</p>

              <h2 className="text-base font-semibold text-gray-900">Violation Consequences</h2>
              <p className="text-gray-600 text-sm leading-relaxed">Unauthorized software purchases will be subject to retrospective review and may result in mandatory offboarding of the software and disciplinary action.</p>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Policy Details</h3>
            <div className="space-y-3 text-sm">
              {[
                { icon: Tag, label: 'Category', value: 'IT & Security' },
                { icon: User, label: 'Owner', value: 'CTO Office' },
                { icon: Clock, label: 'Effective Date', value: '2024-01-01' },
                { icon: Clock, label: 'Review Date', value: '2025-01-01' },
                { icon: BookOpen, label: 'Version', value: '2.3' },
              ].map(d => (
                <div key={d.label} className="flex items-center gap-2">
                  <d.icon className="w-4 h-4 text-gray-600 shrink-0" />
                  <span className="text-gray-500 w-24 shrink-0">{d.label}</span>
                  <span className="text-gray-600">{d.value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Exception Stats</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Total exceptions</span>
                <span className="text-gray-900 font-medium">12</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Approval rate</span>
                <span className="text-green-700 font-medium">75%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Drift score</span>
                <span className="text-red-600 font-medium">High</span>
              </div>
            </div>
            <button onClick={() => navigate('/app/insights/policy-drift')} className="flex items-center gap-1 text-xs text-primary hover:text-primary-dark font-medium transition-colors mt-3">
              <TrendingUp className="w-3 h-3" /> View drift analysis
            </button>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Quick Actions</h3>
            <div className="space-y-2">
              <button onClick={() => navigate('/app/policies/simulator')} className="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-50 hover:bg-gray-100 text-gray-600 text-sm transition-colors">
                <Shield className="w-4 h-4 text-primary" /> Test in Simulator
              </button>
              <button onClick={() => navigate(`/app/policies/${policyId}/versions`)} className="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-50 hover:bg-gray-100 text-gray-600 text-sm transition-colors">
                <Clock className="w-4 h-4 text-primary" /> View Version History
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
