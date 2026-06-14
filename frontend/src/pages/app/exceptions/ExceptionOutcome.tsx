import { CheckCircle, Calendar, User, AlertTriangle } from 'lucide-react'

const conditions = [
  { text: 'CISO security sign-off required within 24 hours', status: 'pending' },
  { text: 'License limited to 90 days (expires March 18, 2025)', status: 'active' },
  { text: 'Full procurement to be completed in parallel', status: 'in_progress' },
  { text: 'Usage restricted to design team (max 8 seats)', status: 'active' },
]

const statusConfig = {
  pending: { label: 'Pending', class: 'bg-yellow-50 text-yellow-700 ring-1 ring-yellow-600/20' },
  active: { label: 'Active', class: 'bg-green-50 text-green-700 ring-1 ring-green-600/20' },
  in_progress: { label: 'In Progress', class: 'bg-blue-50 text-blue-700 ring-1 ring-blue-600/20' },
  completed: { label: 'Completed', class: 'bg-gray-100 text-gray-700 ring-1 ring-gray-300' },
}

export default function ExceptionOutcome() {
  return (
    <div className="fade-in space-y-6">
      {/* Result banner */}
      <div className="bg-green-500/5 border border-green-500/30 rounded-xl p-6 flex items-center gap-4">
        <div className="w-14 h-14 rounded-2xl bg-green-500/10 flex items-center justify-center shrink-0">
          <CheckCircle className="w-8 h-8 text-green-600" />
        </div>
        <div>
          <div className="text-xs text-green-700 font-semibold mb-1 uppercase tracking-wide">Exception Approved</div>
          <div className="text-xl font-bold text-gray-900 mb-1">Approved with Conditions</div>
          <div className="flex items-center gap-3 text-xs text-gray-500">
            <span className="flex items-center gap-1"><User className="w-3 h-3" />Decided by Sarah Chen (VP Operations)</span>
            <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />December 18, 2024 at 3:42 PM</span>
          </div>
        </div>
      </div>

      {/* Decision rationale */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Decision Rationale</h3>
        <p className="text-sm text-gray-600 leading-relaxed">
          Approved based on the significant and quantifiable business impact ($120K revenue risk), strong precedent alignment (PREC-0234),
          and the genuine time constraint created by the executive-approved accelerated launch. The vendor is already vetted and security-approved.
          Conditions are in place to mitigate the identified risks around pattern behavior and CISO oversight.
        </p>
      </div>

      {/* Conditions tracking */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-4 h-4 text-yellow-600" />
          <h3 className="text-sm font-semibold text-gray-900">Conditions Tracking</h3>
        </div>
        <div className="space-y-3">
          {conditions.map((c, i) => {
            const cfg = statusConfig[c.status as keyof typeof statusConfig]
            return (
              <div key={i} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm text-gray-600">{c.text}</p>
                </div>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${cfg.class}`}>{cfg.label}</span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Next steps */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Next Steps</h3>
        <div className="space-y-2 text-sm text-gray-500">
          <p>1. Requester (Alex Turner) has been notified of the approval</p>
          <p>2. CISO calendar invite sent for security sign-off (due Dec 19)</p>
          <p>3. Vendor provisioning request submitted</p>
          <p>4. Procurement team notified to begin standard 30-day process</p>
          <p>5. This case will be automatically archived after 90 days</p>
        </div>
      </div>
    </div>
  )
}
