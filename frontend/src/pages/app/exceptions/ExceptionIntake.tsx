import { FileText, Building2, User, Tag, DollarSign, Calendar, AlertTriangle } from 'lucide-react'

const fields = [
  { label: 'Exception Title', value: 'Emergency software license for design team', icon: FileText },
  { label: 'Category', value: 'IT & Security', icon: Tag },
  { label: 'Department', value: 'Product Design', icon: Building2 },
  { label: 'Requested By', value: 'Alex Turner (alex.turner@company.com)', icon: User },
  { label: 'Financial Amount', value: '$4,500 / year', icon: DollarSign },
  { label: 'Decision Deadline', value: 'December 20, 2024', icon: Calendar },
  { label: 'Priority', value: 'High', icon: AlertTriangle },
]

export default function ExceptionIntake() {
  return (
    <div className="fade-in space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {fields.map(f => (
          <div key={f.label} className="bg-dark2 rounded-xl border border-white/10 p-4">
            <div className="flex items-center gap-2 mb-1">
              <f.icon className="w-4 h-4 text-gray-500" />
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">{f.label}</span>
            </div>
            <p className="text-sm text-white font-medium">{f.value}</p>
          </div>
        ))}
      </div>

      <div className="bg-dark2 rounded-xl border border-white/10 p-6">
        <h3 className="text-sm font-semibold text-white mb-3">Business Justification</h3>
        <p className="text-sm text-gray-300 leading-relaxed">
          The design team requires immediate access to advanced prototyping tools (Figma Enterprise + Principle) to meet the Q1 product launch deadline.
          Current policy requires a 30-day procurement process, but the project timeline allows only 5 days due to an accelerated launch schedule.
        </p>
        <p className="text-sm text-gray-300 leading-relaxed mt-3">
          Without this exception, the design team will be blocked from completing high-fidelity prototypes required for stakeholder sign-off.
          Estimated business impact of delay: $120,000 in delayed revenue and potential loss of a key enterprise customer.
        </p>
        <p className="text-sm text-gray-300 leading-relaxed mt-3">
          We are requesting a 90-day emergency license while the standard procurement process is completed in parallel.
          The vendor has confirmed availability and can provision access within 24 hours of approval.
        </p>
      </div>

      <div className="bg-dark2 rounded-xl border border-white/10 p-6">
        <h3 className="text-sm font-semibold text-white mb-3">Policy Being Excepted</h3>
        <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
          <FileText className="w-5 h-5 text-primary shrink-0" />
          <div>
            <div className="text-sm font-medium text-white">IT Software Procurement Policy v2.3</div>
            <div className="text-xs text-gray-500">Section 4.2 — Standard procurement requires 30-day minimum review period</div>
          </div>
        </div>
      </div>
    </div>
  )
}
