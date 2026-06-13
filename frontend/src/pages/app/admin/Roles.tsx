import { Shield, Plus } from 'lucide-react'

const roles = [
  { name: 'Owner', users: 1, desc: 'Full access to all features and settings', perms: ['All permissions'] },
  { name: 'Admin', users: 3, desc: 'Manage organization, users, and all exceptions', perms: ['Manage users', 'Manage policies', 'Approve exceptions', 'View analytics'] },
  { name: 'Manager', users: 8, desc: 'Approve exceptions and manage team workflows', perms: ['Approve exceptions', 'View team analytics', 'Manage escalations'] },
  { name: 'Approver', users: 12, desc: 'Review and decide on assigned exceptions', perms: ['Approve assigned exceptions', 'View policies', 'View precedents'] },
  { name: 'Submitter', users: 28, desc: 'Submit exception requests', perms: ['Submit exceptions', 'View own exceptions', 'View policies'] },
  { name: 'Viewer', users: 5, desc: 'Read-only access to exceptions and policies', perms: ['View exceptions', 'View policies'] },
]

export default function Roles() {
  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Shield className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold text-white">Roles & Permissions</h1>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" /> Custom Role
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {roles.map(r => (
          <div key={r.name} className="bg-dark2 rounded-xl border border-white/10 p-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-white">{r.name}</span>
              <span className="text-xs text-gray-500">{r.users} users</span>
            </div>
            <p className="text-xs text-gray-400 mb-3">{r.desc}</p>
            <div className="flex flex-wrap gap-1.5">
              {r.perms.map(p => (
                <span key={p} className="px-2 py-0.5 rounded text-xs bg-white/5 text-gray-400 border border-white/5">{p}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
