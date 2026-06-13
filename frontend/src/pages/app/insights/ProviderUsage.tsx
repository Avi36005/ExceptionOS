import { Activity } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const usageData = [
  { name: 'Policy Analysis', calls: 847 },
  { name: 'Precedent Search', calls: 623 },
  { name: 'AI Debate', calls: 412 },
  { name: 'Recommendation', calls: 398 },
  { name: 'Form AutoFill', calls: 287 },
  { name: 'Memory Query', calls: 234 },
]

export default function ProviderUsage() {
  return (
    <div className="fade-in">
      <div className="flex items-center gap-3 mb-6">
        <Activity className="w-6 h-6 text-primary" />
        <div>
          <h1 className="text-2xl font-bold text-white">AI Provider Usage</h1>
          <p className="text-gray-400 text-sm mt-1">Usage analytics for AI features across the platform.</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { label: 'Total AI Calls', value: '2,801', change: '+23% vs last month' },
          { label: 'Avg Response Time', value: '1.2s', change: '-0.3s vs last month' },
          { label: 'AI Acceptance Rate', value: '84%', change: 'Users accepting AI recommendations' },
        ].map(s => (
          <div key={s.label} className="bg-dark2 rounded-xl border border-white/10 p-5">
            <div className="text-xs text-gray-500 mb-2">{s.label}</div>
            <div className="text-2xl font-bold text-white mb-1">{s.value}</div>
            <div className="text-xs text-gray-500">{s.change}</div>
          </div>
        ))}
      </div>

      <div className="bg-dark2 rounded-xl border border-white/10 p-6">
        <h2 className="text-sm font-semibold text-white mb-4">AI Feature Usage Breakdown</h2>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={usageData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis type="number" tick={{ fill: '#6B7280', fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="name" tick={{ fill: '#9CA3AF', fontSize: 12 }} axisLine={false} tickLine={false} width={120} />
            <Tooltip contentStyle={{ backgroundColor: '#0C0F24', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#F4F5FA' }} />
            <Bar dataKey="calls" fill="#5B5BF0" radius={[0, 4, 4, 0]} name="API Calls" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
