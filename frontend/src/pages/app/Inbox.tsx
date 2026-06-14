import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Inbox as InboxIcon, Bell, CheckCircle, Clock, AlertTriangle, Filter, Search } from 'lucide-react'
import EmptyState from '../../components/ui/EmptyState'
import { demoNotifications } from '../../lib/demoData'

const mockNotifications = demoNotifications()

const typeConfig = {
  approval_needed: { icon: Clock, color: 'text-yellow-600', bg: 'bg-yellow-500/10' },
  approved: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-500/10' },
  escalated: { icon: AlertTriangle, color: 'text-orange-600', bg: 'bg-orange-500/10' },
  comment: { icon: InboxIcon, color: 'text-blue-600', bg: 'bg-blue-500/10' },
  rejected: { icon: CheckCircle, color: 'text-red-600', bg: 'bg-red-500/10' },
  sla: { icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-500/10' },
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
          <h1 className="text-2xl font-bold text-gray-900">Inbox</h1>
          <p className="text-sm text-gray-500 mt-1">{unreadCount} unread notifications</p>
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
            className="w-full bg-gray-50 border border-gray-200 rounded-lg pl-9 pr-3 py-2 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/30 transition-all" />
        </div>
        <div className="flex items-center gap-1 bg-gray-50 rounded-lg border border-gray-200 p-1">
          {(['all', 'unread'] as const).map(f => (
            <button key={f} onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium capitalize transition-all ${filter === f ? 'bg-primary text-white' : 'text-gray-500 hover:text-gray-900'}`}>
              {f} {f === 'unread' && unreadCount > 0 ? `(${unreadCount})` : ''}
            </button>
          ))}
        </div>
        <button className="p-2 rounded-lg bg-gray-50 border border-gray-200 text-gray-500 hover:text-gray-900 transition-colors">
          <Filter className="w-4 h-4" />
        </button>
      </div>

      {/* Notifications */}
      {filtered.length === 0 ? (
        <EmptyState icon={Bell} title="All caught up!" description="No notifications to show." />
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
          {filtered.map(n => {
            const cfg = typeConfig[n.type as keyof typeof typeConfig]
            const Icon = cfg.icon
            return (
              <div
                key={n.id}
                className={`flex gap-4 p-4 hover:bg-gray-50 cursor-pointer transition-colors ${n.unread ? 'bg-primary/3' : ''}`}
                onClick={() => navigate(`/app/exceptions/${n.exceptionId}/intake`)}
              >
                <div className={`w-9 h-9 rounded-lg ${cfg.bg} flex items-center justify-center shrink-0`}>
                  <Icon className={`w-4 h-4 ${cfg.color}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-sm font-medium text-gray-900">{n.title}</span>
                    {n.unread && <span className="w-1.5 h-1.5 bg-primary rounded-full shrink-0" />}
                  </div>
                  <p className="text-xs text-gray-500 leading-relaxed">{n.body}</p>
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
