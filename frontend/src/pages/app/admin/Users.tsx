import { Users as UsersIcon, Mail } from 'lucide-react'
import { useState } from 'react'

const users = [
  { id: '1', name: 'Sarah Chen', email: 'sarah@acme.com', role: 'admin', dept: 'Operations', status: 'active', lastActive: '2 min ago' },
  { id: '2', name: 'Marcus Williams', email: 'marcus@acme.com', role: 'manager', dept: 'Finance', status: 'active', lastActive: '1h ago' },
  { id: '3', name: 'Priya Patel', email: 'priya@acme.com', role: 'approver', dept: 'HR', status: 'active', lastActive: '3h ago' },
  { id: '4', name: 'Alex Turner', email: 'alex@acme.com', role: 'submitter', dept: 'Product Design', status: 'active', lastActive: '1d ago' },
  { id: '5', name: 'Jane Kim', email: 'jane@acme.com', role: 'viewer', dept: 'Legal', status: 'inactive', lastActive: '2w ago' },
]

const roleColors: Record<string, string> = {
  owner: 'bg-purple-50 text-purple-700 ring-1 ring-purple-200',
  admin: 'bg-primary/10 text-primary ring-1 ring-primary/20',
  manager: 'bg-blue-50 text-blue-700 ring-1 ring-blue-200',
  approver: 'bg-green-50 text-green-700 ring-1 ring-green-200',
  submitter: 'bg-yellow-50 text-yellow-700 ring-1 ring-yellow-200',
  viewer: 'bg-gray-100 text-gray-700 ring-1 ring-gray-200',
}

export default function Users() {
  const [search, setSearch] = useState('')
  const filtered = users.filter(u => !search || u.name.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <UsersIcon className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold text-gray-900">Users</h1>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-sm font-medium transition-colors">
          <Mail className="w-4 h-4" /> Invite User
        </button>
      </div>
      <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search users..."
        className="w-full max-w-sm bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all mb-4" />
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-gray-200">
            {['User', 'Email', 'Role', 'Department', 'Status', 'Last Active'].map(h => (
              <th key={h} className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
            ))}
          </tr></thead>
          <tbody>
            {filtered.map(u => (
              <tr key={u.id} className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors">
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary">{u.name[0]}</div>
                    <span className="text-gray-900 font-medium">{u.name}</span>
                  </div>
                </td>
                <td className="py-3 px-4 text-gray-500">{u.email}</td>
                <td className="py-3 px-4"><span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${roleColors[u.role]}`}>{u.role}</span></td>
                <td className="py-3 px-4 text-gray-500">{u.dept}</td>
                <td className="py-3 px-4"><span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${u.status === 'active' ? 'bg-green-50 text-green-700 ring-1 ring-green-200' : 'bg-gray-100 text-gray-700 ring-1 ring-gray-200'}`}>{u.status}</span></td>
                <td className="py-3 px-4 text-gray-500 text-xs">{u.lastActive}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
