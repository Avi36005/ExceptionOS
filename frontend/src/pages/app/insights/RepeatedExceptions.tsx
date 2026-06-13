import { AlertTriangle, RefreshCw } from 'lucide-react'

const patterns = [
  { pattern: 'IT Emergency Software License', count: 8, category: 'IT', lastSeen: '2024-12-18', recommendation: 'Update IT procurement threshold or create express track' },
  { pattern: 'Senior Engineer Rate Exception', count: 6, category: 'HR', lastSeen: '2024-12-10', recommendation: 'Create Senior Engineering Rate Tier policy' },
  { pattern: 'Budget Carryover Q4→Q1', count: 5, category: 'Finance', lastSeen: '2024-12-01', recommendation: 'Add Q4 carryover provision to Budget Authorization Policy' },
  { pattern: 'NDA Waiver for Startup Vendors', count: 4, category: 'Legal', lastSeen: '2024-11-28', recommendation: 'Create simplified NDA for startups under $500K contract value' },
]

export default function RepeatedExceptions() {
  return (
    <div className="fade-in">
      <h1 className="text-2xl font-bold text-white mb-2">Repeated Exception Patterns</h1>
      <p className="text-gray-400 text-sm mb-6">Exceptions that recur frequently may indicate policies that need updating.</p>
      <div className="space-y-4">
        {patterns.map(p => (
          <div key={p.pattern} className="bg-dark2 rounded-xl border border-white/10 p-5">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-xl bg-yellow-500/10 flex items-center justify-center shrink-0">
                <RefreshCw className="w-5 h-5 text-yellow-400" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h3 className="text-sm font-semibold text-white">{p.pattern}</h3>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">{p.category}</span>
                    <span className="px-2 py-0.5 rounded-md text-xs bg-yellow-500/20 text-yellow-400 font-medium">{p.count}x this quarter</span>
                  </div>
                </div>
                <p className="text-xs text-gray-500 mb-2">Last seen: {p.lastSeen}</p>
                <div className="flex items-start gap-2 p-3 bg-primary/5 border border-primary/20 rounded-lg">
                  <AlertTriangle className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
                  <p className="text-xs text-gray-300"><span className="text-primary font-medium">Recommendation: </span>{p.recommendation}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
