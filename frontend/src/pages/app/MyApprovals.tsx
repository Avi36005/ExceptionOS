import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckSquare, Search, Clock, AlertTriangle } from 'lucide-react'
import toast from 'react-hot-toast'
import StatusBadge from '../../components/ui/StatusBadge'
import EmptyState from '../../components/ui/EmptyState'
import { pendingCases, decidedCases, priorityPill as priorityColor } from '../../lib/demoData'
import { slackNotify } from '../../lib/slack'

function notifyDecision(c: { id: string; title: string; amount: string }, decision: 'approved' | 'rejected') {
  slackNotify({ event: decision, case_id: c.id, title: c.title, amount: c.amount, actor: 'You' })
    .then(() => toast.success(`Sent to Slack: ${c.id} ${decision}`))
    .catch(() => {/* Slack is best-effort; never block the decision */})
}

const pending = pendingCases().map(c => ({
  id: c.id, title: c.title, category: c.category, submitter: c.submitter,
  submitted: c.created, deadline: c.deadline, priority: c.priority, amount: c.amount,
}))

const history = decidedCases().map(c => ({
  id: c.id, title: c.title, category: c.category, submitter: c.submitter,
  decided: c.created, status: c.status,
}))

export default function MyApprovals() {
  const navigate = useNavigate()
  const [tab, setTab] = useState<'pending' | 'history'>('pending')
  const [search, setSearch] = useState('')

  const filteredPending = pending.filter(r => !search || r.title.toLowerCase().includes(search.toLowerCase()))
  const filteredHistory = history.filter(r => !search || r.title.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Approvals</h1>
          <p className="text-sm text-gray-500 mt-1">{pending.length} pending decisions</p>
        </div>
        {pending.length > 0 && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-yellow-50 border border-yellow-600/20">
            <Clock className="w-4 h-4 text-yellow-600" />
            <span className="text-xs text-yellow-700 font-medium">{pending.length} awaiting your decision</span>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 border-b border-gray-200 mb-4">
        {[{ id: 'pending', label: `Pending (${pending.length})` }, { id: 'history', label: 'Decision History' }].map(t => (
          <button key={t.id} onClick={() => setTab(t.id as typeof tab)}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-all ${tab === t.id ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-900'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Search */}
      <div className="relative mb-4 max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search exceptions..."
          className="w-full bg-gray-50 border border-gray-200 rounded-lg pl-9 pr-3 py-2 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
      </div>

      {tab === 'pending' ? (
        <div className="space-y-3">
          {filteredPending.length === 0 ? (
            <EmptyState icon={CheckSquare} title="No pending approvals" description="You're all caught up! No exceptions are waiting for your decision." />
          ) : filteredPending.map(r => (
            <div key={r.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:border-primary/30 cursor-pointer transition-all"
              onClick={() => navigate(`/app/exceptions/${r.id}/intake`)}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs text-primary font-mono">{r.id}</span>
                    <span className={`px-2 py-0.5 rounded-md text-xs font-medium ${priorityColor[r.priority]}`}>{r.priority}</span>
                  </div>
                  <h3 className="text-sm font-semibold text-gray-900 mb-1">{r.title}</h3>
                  <div className="flex items-center gap-3 text-xs text-gray-500">
                    <span>By {r.submitter}</span>
                    <span>·</span>
                    <span>{r.category}</span>
                    <span>·</span>
                    <span>{r.amount}</span>
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <div className="text-xs text-gray-500 mb-2">Deadline</div>
                  <div className="flex items-center gap-1 text-xs text-orange-600 font-medium">
                    <AlertTriangle className="w-3 h-3" />
                    {r.deadline}
                  </div>
                </div>
              </div>
              <div className="flex gap-2 mt-4 pt-4 border-t border-gray-100">
                <button onClick={e => { e.stopPropagation(); notifyDecision(r, 'approved'); navigate(`/app/exceptions/${r.id}/decision`) }}
                  className="flex-1 py-2 rounded-lg bg-green-600 hover:bg-green-700 text-white text-sm font-medium transition-colors">
                  Approve
                </button>
                <button onClick={e => { e.stopPropagation(); navigate(`/app/exceptions/${r.id}/decision`) }}
                  className="flex-1 py-2 rounded-lg bg-gray-100 hover:bg-gray-100 text-gray-900 text-sm font-medium border border-gray-200 transition-colors">
                  Review
                </button>
                <button onClick={e => { e.stopPropagation(); notifyDecision(r, 'rejected'); navigate(`/app/exceptions/${r.id}/decision`) }}
                  className="flex-1 py-2 rounded-lg bg-red-50 hover:bg-red-100 text-red-700 text-sm font-medium transition-colors">
                  Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
          {filteredHistory.map(r => (
            <div key={r.id} className="flex items-center gap-4 p-4 hover:bg-gray-50 cursor-pointer transition-colors"
              onClick={() => navigate(`/app/exceptions/${r.id}/intake`)}>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-xs text-primary font-mono">{r.id}</span>
                  <span className="text-xs text-gray-500">{r.category}</span>
                </div>
                <p className="text-sm text-gray-900 font-medium truncate">{r.title}</p>
                <p className="text-xs text-gray-500 mt-0.5">By {r.submitter} · Decided {r.decided}</p>
              </div>
              <StatusBadge status={r.status} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
