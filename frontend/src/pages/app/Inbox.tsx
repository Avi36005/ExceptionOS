import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Inbox as InboxIcon, Bell, CheckCircle, Clock, AlertTriangle, Filter, Search } from 'lucide-react'
import EmptyState from '../../components/ui/EmptyState'

const mockNotifications = [
  { id: 1, type: 'approval_needed', title: 'Exception requires your approval', body: 'EXC-1048: Emergency software license for design team is pending your decision.', time: '2 hours ago', unread: true, exceptionId: 'EXC-1048' },
  { id: 2, type: 'approved', title: 'Your exception was approved', body: 'EXC-1045: Budget transfer between Q4 projects was approved by Marcus Williams.', time: '4 hours ago', unread: true, exceptionId: 'EXC-1045' },
  { id: 3, type: 'escalated', title: 'Exception escalated to you', body: 'EXC-1042: Contractor rate above policy maximum has been escalated for your review.', time: '6 hours ago', unread: false, exceptionId: 'EXC-1042' },
  { id: 4, type: 'comment', title: 'New comment on your exception', body: 'Sarah Chen commented on EXC-1040: "I need additional documentation before I can approve this."', time: '1 day ago', unread: false, exceptionId: 'EXC-1040' },
  { id: 5, type: 'rejected', title: 'Exception rejected', body: 'EXC-1038: Vendor NDA waiver was rejected. See the decision rationale for details.', time: '2 days ago', unread: false, exceptionId: 'EXC-1038' },
  { id: 6, type: 'sla', title: 'SLA Warning', body: 'EXC-1035 is approaching its deadline. Decision required within 4 hours.', time: '2 days ago', unread: false, exceptionId: 'EXC-1035' },
]

const typeConfig = {
  approval_needed: { icon: Clock, color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
  approved: { icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-500/10' },
  escalated: { icon: AlertTriangle, color: 'text-orange-400', bg: 'bg-orange-500/10' },
  comment: { icon: InboxIcon, color: 'text-blue-400', bg: 'bg-blue-500/10' },
  rejected: { icon: CheckCircle, color: 'text-red-400', bg: 'bg-red-500/10' },
  sla: { icon: AlertTriangle, color: 'text-red-400', bg: 'bg-red-500/10' },
}

export default function Inbox() {
  const navigate = useNavigate()
  const [filter, setFilter] = useState<'all' | 'unread'>('all')
  const [search, setSearch] = useState('')

  const filtered = mockNotifications
    .filter(n => filter === 'all' || n.unread)
    .filter(n => !search || n.title.toLowerCase().includes(search.toLowerCase()) || n.body.toLowerCase().includes(search.toLowerCase()))

  const unreadCount = mockNotifications.filter(n => n.unread).length

  return (
    <div className="fade-in max-w-3xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Inbox</h1>
          <p className="text-sm text-gray-400 mt-1">{unreadCount} unread notifications</p>
        </div>
        {unreadCount > 0 && (
          <button className="text-sm text-primary hover:text-primary-dark font-medium transition-colors">
            Mark all as read
          </button>
        )}
      </div>

      {/* Controls */}
      <div className="flex items-center gap-3 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search notifications..."
            className="w-full bg-white/5 border border-white/10 rounded-lg pl-9 pr-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/30 transition-all" />
        </div>
        <div className="flex items-center gap-1 bg-white/5 rounded-lg border border-white/10 p-1">
          {(['all', 'unread'] as const).map(f => (
            <button key={f} onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium capitalize transition-all ${filter === f ? 'bg-primary text-white' : 'text-gray-400 hover:text-white'}`}>
              {f} {f === 'unread' && unreadCount > 0 ? `(${unreadCount})` : ''}
            </button>
          ))}
        </div>
        <button className="p-2 rounded-lg bg-white/5 border border-white/10 text-gray-400 hover:text-white transition-colors">
          <Filter className="w-4 h-4" />
        </button>
      </div>

      {/* Notifications */}
      {filtered.length === 0 ? (
        <EmptyState icon={Bell} title="All caught up!" description="No notifications to show." />
      ) : (
        <div className="bg-dark2 rounded-xl border border-white/10 divide-y divide-white/5">
          {filtered.map(n => {
            const cfg = typeConfig[n.type as keyof typeof typeConfig]
            const Icon = cfg.icon
            return (
              <div
                key={n.id}
                className={`flex gap-4 p-4 hover:bg-white/3 cursor-pointer transition-colors ${n.unread ? 'bg-primary/3' : ''}`}
                onClick={() => navigate(`/app/exceptions/${n.exceptionId}/intake`)}
              >
                <div className={`w-9 h-9 rounded-lg ${cfg.bg} flex items-center justify-center shrink-0`}>
                  <Icon className={`w-4 h-4 ${cfg.color}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-sm font-medium text-white">{n.title}</span>
                    {n.unread && <span className="w-1.5 h-1.5 bg-primary rounded-full shrink-0" />}
                  </div>
                  <p className="text-xs text-gray-400 leading-relaxed">{n.body}</p>
                  <p className="text-xs text-gray-600 mt-1">{n.time}</p>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
