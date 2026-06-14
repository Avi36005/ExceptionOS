import { TrendingUp, AlertTriangle } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const driftData = [
  { policy: 'IT Procurement', exceptions: 12, threshold: 3 },
  { policy: 'Budget Auth', exceptions: 15, threshold: 5 },
  { policy: 'Remote Work', exceptions: 5, threshold: 4 },
  { policy: 'Vendor NDA', exceptions: 7, threshold: 5 },
  { policy: 'Contractor Rate', exceptions: 3, threshold: 3 },
]

export default function PolicyDrift() {
  return (
    <div className="fade-in space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Policy Drift Analysis</h1>
        <p className="text-gray-500 text-sm">Policies where exception volume signals potential need for policy revision.</p>
      </div>

      <div className="flex items-center gap-3 p-4 bg-red-500/5 border border-red-500/20 rounded-xl">
        <AlertTriangle className="w-5 h-5 text-red-600 shrink-0" />
        <div>
          <div className="text-sm font-semibold text-gray-900">2 policies showing high drift</div>
          <div className="text-xs text-gray-500 mt-0.5">Budget Authorization Policy and IT Procurement Policy are receiving exceptions at 3x the normal rate. Consider policy revision.</div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-primary" />
          <h2 className="text-sm font-semibold text-gray-900">Exception Volume vs. Threshold</h2>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={driftData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
            <XAxis type="number" tick={{ fill: '#6B7280', fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="policy" tick={{ fill: '#9CA3AF', fontSize: 12 }} axisLine={false} tickLine={false} width={110} />
            <Tooltip contentStyle={{ backgroundColor: '#0C0F24', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#F4F5FA' }} />
            <Bar dataKey="exceptions" fill="#5B5BF0" radius={[0, 4, 4, 0]} name="Exceptions" />
            <Bar dataKey="threshold" fill="rgba(239,68,68,0.4)" radius={[0, 4, 4, 0]} name="Threshold" />
          </BarChart>
        </ResponsiveContainer>
        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
          <span className="flex items-center gap-1"><span className="w-3 h-2 rounded bg-primary inline-block" />Actual exceptions</span>
          <span className="flex items-center gap-1"><span className="w-3 h-2 rounded bg-red-500/40 inline-block" />Alert threshold</span>
        </div>
      </div>
    </div>
  )
}
