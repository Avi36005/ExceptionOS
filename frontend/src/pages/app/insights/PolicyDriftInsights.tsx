import { TrendingUp, AlertTriangle } from 'lucide-react'

export default function PolicyDriftInsights() {
  return (
    <div className="fade-in">
      <h1 className="text-2xl font-bold text-white mb-2">Policy Drift Insights</h1>
      <p className="text-gray-400 text-sm mb-6">Policies receiving disproportionate exception volume relative to their baseline.</p>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {[
          { id: 'POL-IT-004', title: 'IT Software Procurement', exceptions: 12, threshold: 3, drift: 'critical' },
          { id: 'POL-FIN-008', title: 'Budget Authorization', exceptions: 15, threshold: 5, drift: 'high' },
          { id: 'POL-VEN-003', title: 'Vendor NDA Requirements', exceptions: 7, threshold: 5, drift: 'medium' },
          { id: 'POL-HR-002', title: 'Remote Work Equipment', exceptions: 5, threshold: 4, drift: 'low' },
        ].map(p => (
          <div key={p.id} className="bg-dark2 rounded-xl border border-white/10 p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono text-primary">{p.id}</span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${
                p.drift === 'critical' ? 'bg-red-500/20 text-red-400' :
                p.drift === 'high' ? 'bg-orange-500/20 text-orange-400' :
                p.drift === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-green-500/20 text-green-400'}`}>{p.drift} drift</span>
            </div>
            <h3 className="text-sm font-semibold text-white mb-3">{p.title}</h3>
            <div className="flex items-center gap-2 mb-2">
              <div className="flex-1 bg-white/10 rounded-full h-2">
                <div className="h-2 rounded-full bg-primary" style={{ width: `${Math.min((p.exceptions / (p.threshold * 2)) * 100, 100)}%` }} />
              </div>
              <span className="text-xs text-gray-400 shrink-0">{p.exceptions}/{p.threshold * 2}</span>
            </div>
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <TrendingUp className="w-3 h-3 text-red-400" />
              {Math.round(p.exceptions / p.threshold)}x above threshold
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
