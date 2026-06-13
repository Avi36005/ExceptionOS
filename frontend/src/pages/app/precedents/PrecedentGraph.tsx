import { Network } from 'lucide-react'

export default function PrecedentGraph() {
  return (
    <div className="fade-in">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Precedent Graph</h1>
        <p className="text-sm text-gray-400 mt-1">Visual relationship map of all precedents and their connections.</p>
      </div>
      <div className="bg-dark2 rounded-2xl border border-white/10 flex items-center justify-center" style={{ height: 500 }}>
        <div className="text-center">
          <Network className="w-16 h-16 text-gray-700 mx-auto mb-4" />
          <p className="text-gray-400 text-sm font-medium">Interactive precedent graph</p>
          <p className="text-gray-600 text-xs mt-1">Connect a graph visualization library to render precedent relationships</p>
          <div className="mt-6 flex flex-wrap gap-2 justify-center">
            {['IT Exceptions', 'HR Exceptions', 'Vendor Exceptions', 'Finance Exceptions'].map(g => (
              <span key={g} className="px-3 py-1 rounded-full bg-white/5 text-gray-400 text-xs border border-white/10">{g}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
