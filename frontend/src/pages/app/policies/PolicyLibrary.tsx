import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BookOpen, Plus, Search, Filter, TrendingUp } from 'lucide-react'
import StatusBadge from '../../../components/ui/StatusBadge'

const policies = [
  { id: 'POL-IT-004', title: 'IT Software Procurement Policy', category: 'IT', version: '2.3', status: 'active' as const, exceptions: 12, drift: 'high', lastUpdated: '2024-10-15' },
  { id: 'POL-IT-001', title: 'Software Security & Vetting Policy', category: 'IT', version: '3.0', status: 'active' as const, exceptions: 8, drift: 'medium', lastUpdated: '2024-09-01' },
  { id: 'POL-HR-002', title: 'Remote Work Equipment Policy', category: 'HR', version: '1.2', status: 'active' as const, exceptions: 5, drift: 'low', lastUpdated: '2024-11-20' },
  { id: 'POL-FIN-008', title: 'Budget Authorization Policy', category: 'Finance', version: '1.5', status: 'active' as const, exceptions: 15, drift: 'medium', lastUpdated: '2024-08-30' },
  { id: 'POL-VEN-003', title: 'Vendor NDA Requirements', category: 'Legal', version: '2.1', status: 'active' as const, exceptions: 7, drift: 'low', lastUpdated: '2024-12-01' },
  { id: 'POL-HR-005', title: 'Contractor Rate Policy', category: 'HR', version: '1.0', status: 'pending' as const, exceptions: 3, drift: 'low', lastUpdated: '2024-12-10' },
]

const driftColors: Record<string, string> = {
  high: 'bg-red-50 text-red-700 ring-1 ring-red-600/20',
  medium: 'bg-yellow-50 text-yellow-700 ring-1 ring-yellow-600/20',
  low: 'bg-green-50 text-green-700 ring-1 ring-green-600/20',
}

export default function PolicyLibrary() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('all')

  const categories = ['all', ...Array.from(new Set(policies.map(p => p.category)))]
  const filtered = policies
    .filter(p => categoryFilter === 'all' || p.category === categoryFilter)
    .filter(p => !search || p.title.toLowerCase().includes(search.toLowerCase()) || p.id.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Policy Library</h1>
          <p className="text-sm text-gray-500 mt-1">{policies.length} active policies</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => navigate('/app/policies/simulator')} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-100 text-gray-900 text-sm font-medium border border-gray-200 transition-colors">
            <TrendingUp className="w-4 h-4" /> Simulator
          </button>
          <button onClick={() => navigate('/app/policies/new')} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-sm font-medium transition-colors">
            <Plus className="w-4 h-4" /> New Policy
          </button>
        </div>
      </div>

      <div className="flex items-center gap-3 mb-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search policies..."
            className="w-full bg-gray-50 border border-gray-200 rounded-lg pl-9 pr-3 py-2 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
        </div>
        <div className="flex gap-1">
          {categories.map(c => (
            <button key={c} onClick={() => setCategoryFilter(c)}
              className={`px-3 py-2 rounded-lg text-xs font-medium capitalize transition-all ${categoryFilter === c ? 'bg-primary/20 text-primary border border-primary/30' : 'bg-gray-50 text-gray-500 hover:text-gray-900 border border-gray-200'}`}>
              {c === 'all' ? 'All' : c}
            </button>
          ))}
        </div>
        <button className="p-2 rounded-lg bg-gray-50 border border-gray-200 text-gray-500 hover:text-gray-900 transition-colors">
          <Filter className="w-4 h-4" />
        </button>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Policy</th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Category</th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Version</th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Exceptions</th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Drift</th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Updated</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(p => (
              <tr key={p.id} className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => navigate(`/app/policies/${p.id}`)}>
                <td className="py-3 px-4 text-primary font-mono text-xs">{p.id}</td>
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-gray-600 shrink-0" />
                    <span className="text-gray-900 font-medium">{p.title}</span>
                  </div>
                </td>
                <td className="py-3 px-4 text-gray-500">{p.category}</td>
                <td className="py-3 px-4 text-gray-500 font-mono text-xs">v{p.version}</td>
                <td className="py-3 px-4"><StatusBadge status={p.status} /></td>
                <td className="py-3 px-4 text-gray-600">{p.exceptions}</td>
                <td className="py-3 px-4"><span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${driftColors[p.drift]}`}>{p.drift}</span></td>
                <td className="py-3 px-4 text-gray-500 text-xs">{p.lastUpdated}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
