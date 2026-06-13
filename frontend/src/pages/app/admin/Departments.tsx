import { Building2, Plus } from 'lucide-react'
import { useState } from 'react'

const departments = [
  { id: '1', name: 'Engineering', head: 'Tom Chen', members: 24, exceptions: 45, approver: 'Sarah Chen' },
  { id: '2', name: 'Product Design', head: 'Alex Turner', members: 8, exceptions: 18, approver: 'Marcus Williams' },
  { id: '3', name: 'Finance', head: 'Marcus Williams', members: 6, exceptions: 31, approver: 'Jane Doe' },
  { id: '4', name: 'Human Resources', head: 'Priya Patel', members: 5, exceptions: 22, approver: 'Sarah Chen' },
  { id: '5', name: 'Legal', head: 'Lisa Wong', members: 4, exceptions: 12, approver: 'Marcus Williams' },
  { id: '6', name: 'Operations', head: 'Sarah Chen', members: 10, exceptions: 28, approver: 'Jane Doe' },
]

export default function Departments() {
  const [search, setSearch] = useState('')
  const filtered = departments.filter(d => !search || d.name.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Building2 className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold text-white">Departments</h1>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" /> Add Department
        </button>
      </div>
      <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search departments..."
        className="w-full max-w-sm bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all mb-4" />
      <div className="bg-dark2 rounded-xl border border-white/10 overflow-hidden">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-white/10">
            {['Department', 'Head', 'Members', 'Exceptions', 'Default Approver'].map(h => (
              <th key={h} className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">{h}</th>
            ))}
          </tr></thead>
          <tbody>
            {filtered.map(d => (
              <tr key={d.id} className="border-b border-white/5 hover:bg-white/3 transition-colors">
                <td className="py-3 px-4 text-white font-medium">{d.name}</td>
                <td className="py-3 px-4 text-gray-400">{d.head}</td>
                <td className="py-3 px-4 text-gray-300">{d.members}</td>
                <td className="py-3 px-4 text-gray-300">{d.exceptions}</td>
                <td className="py-3 px-4 text-gray-400">{d.approver}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
