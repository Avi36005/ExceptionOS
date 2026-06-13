import { Users as UsersIcon, Plus, Mail } from 'lucide-react'
import { useState } from 'react'

const users = [
  { id: '1', name: 'Sarah Chen', email: 'sarah@acme.com', role: 'admin', dept: 'Operations', status: 'active', lastActive: '2 min ago' },
  { id: '2', name: 'Marcus Williams', email: 'marcus@acme.com', role: 'manager', dept: 'Finance', status: 'active', lastActive: '1h ago' },
  { id: '3', name: 'Priya Patel', email: 'priya@acme.com', role: 'approver', dept: 'HR', status: 'active', lastActive: '3h ago' },
  { id: '4', name: 'Alex Turner', email: 'alex@acme.com', role: 'submitter', dept: 'Product Design', status: 'active', lastActive: '1d ago' },
  { id: '5', name: 'Jane Kim', email: 'jane@acme.com', role: 'viewer', dept: 'Legal', status: 'inactive', lastActive: '2w ago' },
]

const roleColors: Record<string, string> = {
  owner: 'bg-purple-500/20 text-purple-400',
  admin: 'bg-primary/20 text-primary',
  manager: 'bg-blue-500/20 text-blue-400',
  approver: 'bg-green-500/20 text-green-400',
  submitter: 'bg-yellow-500/20 text-yellow-400',
  viewer: 'bg-gray-500/20 text-gray-400',
}

export default function Users() {
  const [search, setSearch] = useState('')
  const filtered = users.filter(u => !search || u.name.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <UsersIcon className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold text-white">Users</h1>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-sm font-medium transition-colors">
          <Mail className="w-4 h-4" /> Invite User
        </button>
      </div>
      <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search users..."
        className="w-full max-w-sm bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all mb-4" />
      <div className="bg-dark2 rounded-xl border border-white/10 overflow-hidden">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-white/10">
            {['User', 'Email', 'Role', 'Department', 'Status', 'Last Active'].map(h => (
              <th key={h} className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">{h}</th>
            ))}
          </tr></thead>
          <tbody>
            {filtered.map(u => (
              <tr key={u.id} className="border-b border-white/5 hover:bg-white/3 cursor-pointer transition-colors">
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary">{u.name[0]}</div>
                    <span className="text-white font-medium">{u.name}</span>
                  </div>
                </td>
                <td className="py-3 px-4 text-gray-400">{u.email}</td>
                <td className="py-3 px-4"><span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${roleColors[u.role]}`}>{u.role}</span></td>
                <td className="py-3 px-4 text-gray-400">{u.dept}</td>
                <td className="py-3 px-4"><span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${u.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>{u.status}</span></td>
                <td className="py-3 px-4 text-gray-500 text-xs">{u.lastActive}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
