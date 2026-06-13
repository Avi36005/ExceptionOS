import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Search, Filter, FileText } from 'lucide-react'
import StatusBadge from '../../components/ui/StatusBadge'
import EmptyState from '../../components/ui/EmptyState'

const mockRequests = [
  { id: 'EXC-1048', title: 'Emergency software license for design team', category: 'IT', status: 'under_review' as const, created: '2024-12-18', priority: 'high', approver: 'Sarah Chen' },
  { id: 'EXC-1044', title: 'Vendor NDA waiver for pilot program', category: 'Legal', status: 'approved' as const, created: '2024-12-17', priority: 'medium', approver: 'Marcus Williams' },
  { id: 'EXC-1040', title: 'Remote work equipment reimbursement', category: 'HR', status: 'submitted' as const, created: '2024-12-16', priority: 'low', approver: 'Jane Doe' },
  { id: 'EXC-1035', title: 'Sole-source vendor for Q1 project', category: 'Vendor', status: 'rejected' as const, created: '2024-12-14', priority: 'high', approver: 'Sarah Chen' },
  { id: 'EXC-1030', title: 'Extended contractor agreement', category: 'HR', status: 'approved' as const, created: '2024-12-10', priority: 'medium', approver: 'Marcus Williams' },
  { id: 'EXC-1020', title: 'Budget carryover from Q3', category: 'Finance', status: 'closed' as const, created: '2024-12-01', priority: 'low', approver: 'Jane Doe' },
]

const priorityColor: Record<string, string> = {
  high: 'text-red-400',
  medium: 'text-yellow-400',
  low: 'text-green-400',
}

export default function MyRequests() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  const filtered = mockRequests
    .filter(r => statusFilter === 'all' || r.status === statusFilter)
    .filter(r => !search || r.title.toLowerCase().includes(search.toLowerCase()) || r.id.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">My Requests</h1>
          <p className="text-sm text-gray-400 mt-1">{mockRequests.length} total exceptions submitted</p>
        </div>
        <button onClick={() => navigate('/app/exceptions/new')}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white font-medium text-sm transition-colors">
          <Plus className="w-4 h-4" /> New Exception
        </button>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-3 mb-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search your requests..."
            className="w-full bg-white/5 border border-white/10 rounded-lg pl-9 pr-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
        </div>
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
          className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-primary/60 transition-all">
          <option value="all">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="submitted">Submitted</option>
          <option value="under_review">Under Review</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="closed">Closed</option>
        </select>
        <button className="p-2 rounded-lg bg-white/5 border border-white/10 text-gray-400 hover:text-white transition-colors">
          <Filter className="w-4 h-4" />
        </button>
      </div>

      {/* Table */}
      {filtered.length === 0 ? (
        <EmptyState icon={FileText} title="No requests found" description="You haven't submitted any exceptions yet, or none match your filters." action={
          <button onClick={() => navigate('/app/exceptions/new')} className="btn-primary px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white font-medium text-sm transition-colors flex items-center gap-2">
            <Plus className="w-4 h-4" /> New Exception
          </button>
        } />
      ) : (
        <div className="bg-dark2 rounded-xl border border-white/10 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">ID</th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Title</th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Category</th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Priority</th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Status</th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Approver</th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Submitted</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(r => (
                <tr key={r.id} className="border-b border-white/5 hover:bg-white/3 cursor-pointer transition-colors"
                  onClick={() => navigate(`/app/exceptions/${r.id}/intake`)}>
                  <td className="py-3 px-4 text-primary font-mono text-xs">{r.id}</td>
                  <td className="py-3 px-4 text-white font-medium max-w-xs truncate">{r.title}</td>
                  <td className="py-3 px-4 text-gray-400">{r.category}</td>
                  <td className={`py-3 px-4 text-xs font-medium capitalize ${priorityColor[r.priority]}`}>{r.priority}</td>
                  <td className="py-3 px-4"><StatusBadge status={r.status} /></td>
                  <td className="py-3 px-4 text-gray-400">{r.approver}</td>
                  <td className="py-3 px-4 text-gray-500 text-xs">{r.created}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
