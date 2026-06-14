import { Shield, AlertTriangle, CheckCircle, ExternalLink } from 'lucide-react'

const policyMatches = [
  {
    id: 'POL-IT-004',
    title: 'IT Software Procurement Policy',
    version: '2.3',
    section: '4.2',
    compliance: 'violated',
    summary: 'Standard procurement requires a minimum 30-day review period for software purchases over $1,000.',
    relevance: 98,
  },
  {
    id: 'POL-FIN-008',
    title: 'Budget Authorization Policy',
    version: '1.5',
    section: '3.1',
    compliance: 'compliant',
    summary: 'Emergency purchases under $10,000 may be approved by department head with CFO notification.',
    relevance: 76,
  },
  {
    id: 'POL-IT-001',
    title: 'Software Security & Vetting Policy',
    version: '3.0',
    section: '2.4',
    compliance: 'partial',
    summary: 'All new software must pass security review before deployment. Emergency exceptions require CISO sign-off.',
    relevance: 65,
  },
]

const complianceConfig = {
  violated: { label: 'Policy Violated', icon: AlertTriangle, class: 'text-red-700 bg-red-50 border-red-600/20' },
  compliant: { label: 'Compliant', icon: CheckCircle, class: 'text-green-700 bg-green-50 border-green-600/20' },
  partial: { label: 'Partial Compliance', icon: Shield, class: 'text-yellow-700 bg-yellow-50 border-yellow-600/20' },
}

export default function ExceptionPolicy() {
  return (
    <div className="fade-in space-y-4">
      <div className="flex items-center gap-3 p-4 bg-red-500/5 border border-red-500/20 rounded-xl">
        <AlertTriangle className="w-5 h-5 text-red-600 shrink-0" />
        <div>
          <div className="text-sm font-semibold text-gray-900">Primary Policy Violation Detected</div>
          <div className="text-xs text-gray-500 mt-0.5">This exception request violates 1 active policy and partially conflicts with 1 other. Review below.</div>
        </div>
      </div>

      {policyMatches.map(p => {
        const cfg = complianceConfig[p.compliance as keyof typeof complianceConfig]
        const Icon = cfg.icon
        return (
          <div key={p.id} className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-start justify-between gap-4 mb-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-mono text-primary">{p.id}</span>
                  <span className="text-xs text-gray-500">v{p.version} · Section {p.section}</span>
                  <span className="text-xs text-gray-600">· {p.relevance}% relevant</span>
                </div>
                <h3 className="text-sm font-semibold text-gray-900">{p.title}</h3>
              </div>
              <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-medium shrink-0 ${cfg.class}`}>
                <Icon className="w-3.5 h-3.5" />
                {cfg.label}
              </div>
            </div>
            <p className="text-sm text-gray-600 leading-relaxed mb-3">{p.summary}</p>
            <button className="flex items-center gap-1 text-xs text-primary hover:text-primary-dark font-medium transition-colors">
              View full policy <ExternalLink className="w-3 h-3" />
            </button>
          </div>
        )
      })}
    </div>
  )
}
