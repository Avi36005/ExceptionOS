import { TrendingUp } from 'lucide-react'

export default function PolicyDriftInsights() {
  return (
    <div className="fade-in">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Policy Drift Insights</h1>
      <p className="text-gray-500 text-sm mb-6">Policies receiving disproportionate exception volume relative to their baseline.</p>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {[
          { id: 'POL-IT-004', title: 'IT Software Procurement', exceptions: 12, threshold: 3, drift: 'critical' },
          { id: 'POL-FIN-008', title: 'Budget Authorization', exceptions: 15, threshold: 5, drift: 'high' },
          { id: 'POL-VEN-003', title: 'Vendor NDA Requirements', exceptions: 7, threshold: 5, drift: 'medium' },
          { id: 'POL-HR-002', title: 'Remote Work Equipment', exceptions: 5, threshold: 4, drift: 'low' },
        ].map(p => (
          <div key={p.id} className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono text-primary">{p.id}</span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ring-1 ${
                p.drift === 'critical' ? 'bg-red-50 text-red-700 ring-red-200' :
                p.drift === 'high' ? 'bg-orange-50 text-orange-700 ring-orange-200' :
                p.drift === 'medium' ? 'bg-yellow-50 text-yellow-700 ring-yellow-200' :
                'bg-green-50 text-green-700 ring-green-200'}`}>{p.drift} drift</span>
            </div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">{p.title}</h3>
            <div className="flex items-center gap-2 mb-2">
              <div className="flex-1 bg-gray-100 rounded-full h-2">
                <div className="h-2 rounded-full bg-primary" style={{ width: `${Math.min((p.exceptions / (p.threshold * 2)) * 100, 100)}%` }} />
              </div>
              <span className="text-xs text-gray-500 shrink-0">{p.exceptions}/{p.threshold * 2}</span>
            </div>
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <TrendingUp className="w-3 h-3 text-red-600" />
              {Math.round(p.exceptions / p.threshold)}x above threshold
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
