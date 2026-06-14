import { AlertCircle, Plus } from 'lucide-react'

const rules = [
  { id: 1, name: 'High-value financial exception', trigger: 'Amount > $50,000', escalateTo: 'CFO', timeoutHrs: 48, active: true },
  { id: 2, name: 'Deadline missed', trigger: 'SLA exceeded by 24 hours', escalateTo: 'Department Head', timeoutHrs: 24, active: true },
  { id: 3, name: 'Policy violation - critical', trigger: 'Policy compliance = violated AND priority = critical', escalateTo: 'VP Operations', timeoutHrs: 12, active: true },
  { id: 4, name: 'CISO required', trigger: 'Category = IT AND security_flag = true', escalateTo: 'CISO', timeoutHrs: 24, active: false },
]

export default function EscalationRules() {
  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <AlertCircle className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold text-gray-900">Escalation Rules</h1>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" /> Add Rule
        </button>
      </div>
      <div className="space-y-3">
        {rules.map(r => (
          <div key={r.id} className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-gray-900">{r.name}</h3>
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-500">Escalate after {r.timeoutHrs}h</span>
                <button className={`relative w-9 h-5 rounded-full transition-colors ${r.active ? 'bg-primary' : 'bg-gray-100'}`}>
                  <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-all ${r.active ? 'right-0.5' : 'left-0.5'}`} />
                </button>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-xs text-gray-500 block mb-0.5">Trigger</span>
                <span className="text-gray-600 font-mono text-xs">{r.trigger}</span>
              </div>
              <div>
                <span className="text-xs text-gray-500 block mb-0.5">Escalate To</span>
                <span className="text-gray-600">{r.escalateTo}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
