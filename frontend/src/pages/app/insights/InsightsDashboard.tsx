import { useNavigate } from 'react-router-dom'
import { TrendingUp, AlertTriangle, Brain, Activity, ArrowRight } from 'lucide-react'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

const radarData = [
  { category: 'IT', score: 72 },
  { category: 'HR', score: 85 },
  { category: 'Finance', score: 63 },
  { category: 'Legal', score: 90 },
  { category: 'Vendor', score: 78 },
  { category: 'Operations', score: 88 },
]

const trendData = [
  { month: 'Aug', approvalRate: 78, avgTime: 6.2 },
  { month: 'Sep', approvalRate: 82, avgTime: 5.8 },
  { month: 'Oct', approvalRate: 80, avgTime: 6.5 },
  { month: 'Nov', approvalRate: 85, avgTime: 5.2 },
  { month: 'Dec', approvalRate: 81, avgTime: 6.8 },
]

const insightCards = [
  { icon: TrendingUp, label: 'Policy Drift', value: '2 policies', desc: 'above threshold', color: 'text-red-400', bg: 'bg-red-500/10', to: '/app/insights/policy-drift' },
  { icon: AlertTriangle, label: 'Repeated Exceptions', value: '8 patterns', desc: 'detected this quarter', color: 'text-yellow-400', bg: 'bg-yellow-500/10', to: '/app/insights/repeated' },
  { icon: Brain, label: 'Memory Health', value: '94%', desc: 'coverage score', color: 'text-green-400', bg: 'bg-green-500/10', to: '/app/insights/memory-health' },
  { icon: Activity, label: 'AI Usage', value: '1,247', desc: 'AI assists this month', color: 'text-primary', bg: 'bg-primary/10', to: '/app/insights/providers' },
]

export default function InsightsDashboard() {
  const navigate = useNavigate()

  return (
    <div className="fade-in space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Insights</h1>
        <p className="text-sm text-gray-400 mt-1">AI-powered analysis of your organization's exception patterns and decision quality.</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {insightCards.map(c => (
          <button key={c.label} onClick={() => navigate(c.to)} className="bg-dark2 rounded-xl border border-white/10 p-5 hover:border-primary/30 transition-all text-left">
            <div className={`w-10 h-10 rounded-xl ${c.bg} flex items-center justify-center mb-3`}>
              <c.icon className={`w-5 h-5 ${c.color}`} />
            </div>
            <div className={`text-2xl font-bold ${c.color} mb-1`}>{c.value}</div>
            <div className="text-xs text-gray-500 font-medium">{c.label}</div>
            <div className="text-xs text-gray-600">{c.desc}</div>
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-dark2 rounded-xl border border-white/10 p-6">
          <h2 className="text-sm font-semibold text-white mb-4">Policy Compliance by Category</h2>
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(255,255,255,0.1)" />
              <PolarAngleAxis dataKey="category" tick={{ fill: '#6B7280', fontSize: 11 }} />
              <Radar dataKey="score" stroke="#5B5BF0" fill="#5B5BF0" fillOpacity={0.2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-dark2 rounded-xl border border-white/10 p-6">
          <h2 className="text-sm font-semibold text-white mb-4">Approval Rate Trend</h2>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" tick={{ fill: '#6B7280', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#6B7280', fontSize: 11 }} axisLine={false} tickLine={false} domain={[60, 100]} />
              <Tooltip contentStyle={{ backgroundColor: '#0C0F24', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#F4F5FA' }} />
              <Line type="monotone" dataKey="approvalRate" stroke="#5B5BF0" strokeWidth={2} dot={false} name="Approval Rate %" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-dark2 rounded-xl border border-white/10 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-white">AI Recommendations</h2>
          <button onClick={() => navigate('/app/insights/policy-drift')} className="flex items-center gap-1 text-xs text-primary font-medium transition-colors">
            View all <ArrowRight className="w-3 h-3" />
          </button>
        </div>
        <div className="space-y-3">
          {[
            { level: 'high', text: 'IT Software Procurement Policy is seeing 4x the expected exception volume. Consider raising the budget threshold from $1,000 to $2,500.' },
            { level: 'medium', text: '8 contractor rate exceptions this quarter follow a pattern — 6 are for senior engineers. Consider creating a "Senior Engineering Rate Tier" policy.' },
            { level: 'low', text: 'Q4 approval times increased by 31% — likely due to holiday schedules. Consider pre-approving a list of routine exceptions for Q4.' },
          ].map((r, i) => (
            <div key={i} className="flex gap-3 p-3 bg-white/3 rounded-lg">
              <span className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${r.level === 'high' ? 'bg-red-400' : r.level === 'medium' ? 'bg-yellow-400' : 'bg-green-400'}`} />
              <p className="text-sm text-gray-300">{r.text}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
