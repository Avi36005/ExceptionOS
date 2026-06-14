import { TrendingUp, TrendingDown, Clock, CheckCircle, XCircle, AlertTriangle, Plus, ArrowRight, Brain } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { useAuthStore } from '../../store/authStore'
import { useOrgStore } from '../../store/orgStore'

const areaData = [
  { month: 'Jul', submitted: 34, approved: 28, rejected: 6 },
  { month: 'Aug', submitted: 41, approved: 35, rejected: 6 },
  { month: 'Sep', submitted: 38, approved: 30, rejected: 8 },
  { month: 'Oct', submitted: 52, approved: 44, rejected: 8 },
  { month: 'Nov', submitted: 47, approved: 38, rejected: 9 },
  { month: 'Dec', submitted: 63, approved: 51, rejected: 12 },
]

const categoryData = [
  { name: 'Vendor', count: 24 },
  { name: 'HR', count: 18 },
  { name: 'IT', count: 31 },
  { name: 'Finance', count: 15 },
  { name: 'Legal', count: 9 },
]

const recentExceptions = [
  { id: 'EXC-1048', title: 'Emergency software license for design team', status: 'under_review', category: 'IT', time: '2h ago', priority: 'high' },
  { id: 'EXC-1047', title: 'Contractor rate above policy maximum', status: 'approved', category: 'Vendor', time: '4h ago', priority: 'medium' },
  { id: 'EXC-1046', title: 'Remote work equipment reimbursement', status: 'submitted', category: 'HR', time: '6h ago', priority: 'low' },
  { id: 'EXC-1045', title: 'Budget transfer between Q4 projects', status: 'rejected', category: 'Finance', time: '1d ago', priority: 'high' },
  { id: 'EXC-1044', title: 'Vendor NDA waiver for pilot program', status: 'approved', category: 'Legal', time: '1d ago', priority: 'medium' },
]

const statusMap: Record<string, { label: string; class: string }> = {
  submitted: { label: 'Submitted', class: 'bg-blue-50 text-blue-700 ring-1 ring-blue-200' },
  under_review: { label: 'Under Review', class: 'bg-yellow-50 text-yellow-700 ring-1 ring-yellow-200' },
  approved: { label: 'Approved', class: 'bg-green-50 text-green-700 ring-1 ring-green-200' },
  rejected: { label: 'Rejected', class: 'bg-red-50 text-red-700 ring-1 ring-red-200' },
}

const priorityColors: Record<string, string> = {
  high: 'bg-red-500',
  medium: 'bg-yellow-500',
  low: 'bg-green-500',
}

const stats = [
  { label: 'Open Exceptions', value: '23', change: '+3', up: true, icon: Clock, color: 'text-blue-600' },
  { label: 'Approved This Month', value: '51', change: '+34%', up: true, icon: CheckCircle, color: 'text-green-600' },
  { label: 'Rejected', value: '12', change: '-8%', up: false, icon: XCircle, color: 'text-red-600' },
  { label: 'Escalated', value: '4', change: '+1', up: true, icon: AlertTriangle, color: 'text-orange-600' },
]

export default function Dashboard() {
  const { user } = useAuthStore()
  const { currentOrg } = useOrgStore()
  const navigate = useNavigate()
  const firstName = user?.user_metadata?.full_name?.split(' ')[0] || 'there'

  return (
    <div className="fade-in space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Good morning, {firstName} 👋</h1>
          <p className="text-gray-500 text-sm mt-1">{currentOrg?.name || 'ExceptionOS'} · {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</p>
        </div>
        <button onClick={() => navigate('/app/exceptions/new')}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white font-medium text-sm transition-colors">
          <Plus className="w-4 h-4" /> New Exception
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(s => (
          <div key={s.label} className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs text-gray-500 font-medium uppercase tracking-wide">{s.label}</span>
              <s.icon className={`w-4 h-4 ${s.color}`} />
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">{s.value}</div>
            <div className={`flex items-center gap-1 text-xs font-medium ${s.up ? 'text-green-600' : 'text-red-600'}`}>
              {s.up ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              {s.change} vs last month
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Area chart */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-sm font-semibold text-gray-900">Exception Volume</h2>
              <p className="text-xs text-gray-500 mt-0.5">Last 6 months</p>
            </div>
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-primary" />Submitted</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500" />Approved</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500" />Rejected</span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={areaData}>
              <defs>
                <linearGradient id="colorSubmitted" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#5B5BF0" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#5B5BF0" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
              <XAxis dataKey="month" tick={{ fill: '#6B7280', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#6B7280', fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ backgroundColor: '#0C0F24', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#F4F5FA' }} />
              <Area type="monotone" dataKey="submitted" stroke="#5B5BF0" fill="url(#colorSubmitted)" strokeWidth={2} />
              <Area type="monotone" dataKey="approved" stroke="#22c55e" fill="none" strokeWidth={2} />
              <Area type="monotone" dataKey="rejected" stroke="#ef4444" fill="none" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Bar chart */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="mb-6">
            <h2 className="text-sm font-semibold text-gray-900">By Category</h2>
            <p className="text-xs text-gray-500 mt-0.5">This month</p>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={categoryData} layout="vertical">
              <XAxis type="number" tick={{ fill: '#6B7280', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fill: '#6B7280', fontSize: 12 }} axisLine={false} tickLine={false} width={50} />
              <Tooltip contentStyle={{ backgroundColor: '#0C0F24', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#F4F5FA' }} />
              <Bar dataKey="count" fill="#5B5BF0" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* AI Insight Banner */}
      <div className="bg-gradient-to-r from-primary/10 to-primary/5 border border-primary/20 rounded-xl p-5 flex items-center gap-4">
        <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center shrink-0">
          <Brain className="w-5 h-5 text-primary" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-primary uppercase tracking-wide">Hindsight™ Insight</span>
            <span className="w-1.5 h-1.5 bg-primary rounded-full pulse-dot" />
          </div>
          <p className="text-sm text-gray-600">IT exception volume is up 31% this month — 7 out of 10 involve software licensing. Consider updating your IT procurement policy threshold to reduce repeat exceptions.</p>
        </div>
        <button onClick={() => navigate('/app/insights/policy-drift')} className="flex items-center gap-1 text-xs text-primary hover:text-primary-dark font-medium whitespace-nowrap transition-colors">
          View analysis <ArrowRight className="w-3 h-3" />
        </button>
      </div>

      {/* Recent Exceptions */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-sm font-semibold text-gray-900">Recent Exceptions</h2>
          <button onClick={() => navigate('/app/my-requests')} className="text-xs text-primary hover:text-primary-dark font-medium transition-colors flex items-center gap-1">
            View all <ArrowRight className="w-3 h-3" />
          </button>
        </div>
        <div className="divide-y divide-gray-100">
          {recentExceptions.map(ex => (
            <button
              key={ex.id}
              onClick={() => navigate(`/app/exceptions/${ex.id}/intake`)}
              className="w-full flex items-center gap-4 p-4 hover:bg-gray-50 transition-colors text-left"
            >
              <div className={`w-2 h-2 rounded-full shrink-0 ${priorityColors[ex.priority]}`} />
              <div className="flex-1 min-w-0">
                <div className="text-sm text-gray-900 font-medium truncate">{ex.title}</div>
                <div className="text-xs text-gray-500 mt-0.5">{ex.id} · {ex.category} · {ex.time}</div>
              </div>
              <span className={`px-2 py-0.5 rounded-md text-xs font-medium shrink-0 ${statusMap[ex.status]?.class}`}>
                {statusMap[ex.status]?.label}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
