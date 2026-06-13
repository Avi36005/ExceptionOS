import { DollarSign, Plus } from 'lucide-react'

const budgets = [
  { dept: 'Engineering', allocated: 500000, used: 387000, exceptions: 12 },
  { dept: 'Product Design', allocated: 120000, used: 89000, exceptions: 5 },
  { dept: 'Finance', allocated: 200000, used: 165000, exceptions: 8 },
  { dept: 'HR', allocated: 150000, used: 98000, exceptions: 4 },
  { dept: 'Legal', allocated: 300000, used: 210000, exceptions: 7 },
  { dept: 'Operations', allocated: 250000, used: 198000, exceptions: 9 },
]

export default function Budgets() {
  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <DollarSign className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold text-white">Budget Limits</h1>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" /> Set Budget
        </button>
      </div>
      <div className="space-y-3">
        {budgets.map(b => {
          const pct = (b.used / b.allocated) * 100
          return (
            <div key={b.dept} className="bg-dark2 rounded-xl border border-white/10 p-5">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-white">{b.dept}</h3>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>{b.exceptions} exception requests</span>
                  <span className={`font-semibold ${pct > 90 ? 'text-red-400' : pct > 75 ? 'text-yellow-400' : 'text-green-400'}`}>{pct.toFixed(0)}% used</span>
                </div>
              </div>
              <div className="bg-white/10 rounded-full h-2 mb-2">
                <div className={`h-2 rounded-full transition-all ${pct > 90 ? 'bg-red-500' : pct > 75 ? 'bg-yellow-500' : 'bg-primary'}`} style={{ width: `${pct}%` }} />
              </div>
              <div className="flex justify-between text-xs text-gray-500">
                <span>${b.used.toLocaleString()} used</span>
                <span>${b.allocated.toLocaleString()} allocated</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
