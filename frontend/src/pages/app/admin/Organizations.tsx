import { Building2, Plus } from 'lucide-react'
import { useState } from 'react'

const orgs = [
  { id: '1', name: 'Acme Corporation', slug: 'acme', plan: 'Enterprise', members: 42, exceptions: 156, status: 'active' },
  { id: '2', name: 'TechStartup Inc.', slug: 'techstartup', plan: 'Growth', members: 12, exceptions: 34, status: 'active' },
  { id: '3', name: 'Global Finance Ltd', slug: 'globalfinance', plan: 'Enterprise', members: 88, exceptions: 312, status: 'active' },
]

export default function Organizations() {
  const [search, setSearch] = useState('')
  const filtered = orgs.filter(o => !search || o.name.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Building2 className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold text-gray-900">Organizations</h1>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" /> New Organization
        </button>
      </div>
      <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search organizations..."
        className="w-full max-w-sm bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all mb-4" />
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-gray-200">
            {['Name', 'Slug', 'Plan', 'Members', 'Total Exceptions', 'Status'].map(h => (
              <th key={h} className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
            ))}
          </tr></thead>
          <tbody>
            {filtered.map(o => (
              <tr key={o.id} className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors">
                <td className="py-3 px-4 text-gray-900 font-medium">{o.name}</td>
                <td className="py-3 px-4 text-gray-500 font-mono text-xs">{o.slug}</td>
                <td className="py-3 px-4"><span className="px-2 py-0.5 rounded text-xs bg-primary/20 text-primary font-medium">{o.plan}</span></td>
                <td className="py-3 px-4 text-gray-600">{o.members}</td>
                <td className="py-3 px-4 text-gray-600">{o.exceptions}</td>
                <td className="py-3 px-4"><span className="px-2 py-0.5 rounded text-xs bg-green-50 text-green-700 ring-1 ring-green-600/20 font-medium capitalize">{o.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
