import { Brain, CheckCircle, AlertTriangle } from 'lucide-react'

const healthMetrics = [
  { label: 'Total Precedents', value: '284', status: 'good', desc: 'Across all categories' },
  { label: 'Coverage Score', value: '94%', status: 'good', desc: 'Of exception types have precedent' },
  { label: 'Memory Gaps', value: '3', status: 'warning', desc: 'Categories with < 5 precedents' },
  { label: 'Stale Precedents', value: '12', status: 'warning', desc: 'Decisions older than 2 years' },
  { label: 'Avg Decision Quality', value: '4.2/5', status: 'good', desc: 'Based on outcome tracking' },
  { label: 'Last Sync', value: '2 min ago', status: 'good', desc: 'Memory index up to date' },
]

export default function MemoryHealth() {
  return (
    <div className="fade-in">
      <div className="flex items-center gap-3 mb-6">
        <Brain className="w-6 h-6 text-primary" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Memory Health</h1>
          <p className="text-gray-500 text-sm mt-1">Status of your organization's institutional memory.</p>
        </div>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {healthMetrics.map(m => (
          <div key={m.label} className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-500 font-medium">{m.label}</span>
              {m.status === 'good' ? <CheckCircle className="w-4 h-4 text-green-600" /> : <AlertTriangle className="w-4 h-4 text-yellow-600" />}
            </div>
            <div className={`text-xl font-bold mb-0.5 ${m.status === 'good' ? 'text-gray-900' : 'text-yellow-700'}`}>{m.value}</div>
            <div className="text-xs text-gray-500">{m.desc}</div>
          </div>
        ))}
      </div>
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-sm font-semibold text-gray-900 mb-4">Memory Gaps — Categories Needing More Precedents</h2>
        <div className="space-y-3">
          {[
            { category: 'Operations', precedents: 3, needed: 10 },
            { category: 'Security Incidents', precedents: 2, needed: 8 },
            { category: 'Data Privacy', precedents: 4, needed: 10 },
          ].map(g => (
            <div key={g.category}>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-gray-600">{g.category}</span>
                <span className="text-gray-500">{g.precedents}/{g.needed}</span>
              </div>
              <div className="bg-gray-100 rounded-full h-1.5">
                <div className="h-1.5 rounded-full bg-yellow-500/70" style={{ width: `${(g.precedents / g.needed) * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
