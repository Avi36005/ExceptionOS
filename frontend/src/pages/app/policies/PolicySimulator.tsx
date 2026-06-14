import { useState } from 'react'
import { Shield, Sparkles, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'

const categories = ['IT & Security', 'HR & Employment', 'Vendor & Procurement', 'Finance & Compliance', 'Legal & Contracts']
const amounts = ['Under $1,000', '$1,000-$5,000', '$5,000-$25,000', '$25,000-$100,000', 'Over $100,000']

interface SimResult {
  verdict: 'approve' | 'reject' | 'review'
  confidence: number
  matchedPolicies: string[]
  reasoning: string
}

export default function PolicySimulator() {
  const [form, setForm] = useState({ category: '', amount: '', description: '', urgency: 'normal' })
  const [result, setResult] = useState<SimResult | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSimulate = async () => {
    if (!form.category || !form.description) return
    setLoading(true)
    await new Promise(r => setTimeout(r, 1800))
    setResult({
      verdict: form.urgency === 'emergency' ? 'review' : 'reject',
      confidence: 78,
      matchedPolicies: ['IT Software Procurement Policy v2.3 §4.2', 'Budget Authorization Policy v1.5 §3.1'],
      reasoning: form.urgency === 'emergency'
        ? 'Emergency provision exists (§4.2) but requires CISO sign-off. Review recommended with conditions.'
        : 'Standard procurement timeline is applicable. Exception not warranted under current policy.',
    })
    setLoading(false)
  }

  const verdictConfig = {
    approve: { icon: CheckCircle, color: 'text-green-700', bg: 'bg-green-50 border-green-600/30', label: 'Likely to Approve' },
    reject: { icon: XCircle, color: 'text-red-700', bg: 'bg-red-50 border-red-600/30', label: 'Likely to Reject' },
    review: { icon: AlertTriangle, color: 'text-yellow-700', bg: 'bg-yellow-50 border-yellow-600/30', label: 'Recommend Review' },
  }

  return (
    <div className="fade-in max-w-3xl">
      <div className="flex items-center gap-3 mb-6">
        <Shield className="w-6 h-6 text-primary" />
        <div>
          <h1 className="text-xl font-bold text-gray-900">Policy Simulator</h1>
          <p className="text-sm text-gray-500">Test how your policies would respond to a hypothetical exception request.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">Exception Category</label>
            <select value={form.category} onChange={e => setForm(p => ({ ...p, category: e.target.value }))}
              className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 focus:outline-none focus:border-primary/60 transition-all">
              <option value="">Select category</option>
              {categories.map(c => <option key={c} value={c} className="bg-white">{c}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">Financial Amount</label>
            <select value={form.amount} onChange={e => setForm(p => ({ ...p, amount: e.target.value }))}
              className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 focus:outline-none focus:border-primary/60 transition-all">
              <option value="">Select range</option>
              {amounts.map(a => <option key={a} value={a} className="bg-white">{a}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">Urgency</label>
            <div className="grid grid-cols-3 gap-2">
              {['normal', 'urgent', 'emergency'].map(u => (
                <button key={u} onClick={() => setForm(p => ({ ...p, urgency: u }))}
                  className={`py-2 rounded-lg text-xs font-medium capitalize border transition-all ${form.urgency === u ? 'bg-primary/20 border-primary/50 text-primary' : 'bg-gray-50 border-gray-200 text-gray-500 hover:border-gray-300'}`}>
                  {u}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">Description</label>
            <textarea value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))}
              placeholder="Describe the hypothetical exception scenario..."
              rows={4}
              className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all resize-none" />
          </div>
          <button onClick={handleSimulate} disabled={loading || !form.category || !form.description}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold transition-colors disabled:opacity-50">
            {loading ? <div className="w-4 h-4 border-2 border-gray-300 border-t-white rounded-full animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {loading ? 'Simulating...' : 'Run Simulation'}
          </button>
        </div>

        <div>
          {result ? (
            <div className="space-y-4 fade-in">
              <div className={`p-5 rounded-xl border ${verdictConfig[result.verdict].bg}`}>
                <div className="flex items-center gap-3 mb-2">
                  {(() => { const Ic = verdictConfig[result.verdict].icon; return <Ic className={`w-6 h-6 ${verdictConfig[result.verdict].color}`} /> })()}
                  <div>
                    <div className={`text-lg font-bold ${verdictConfig[result.verdict].color}`}>{verdictConfig[result.verdict].label}</div>
                    <div className="text-xs text-gray-500">{result.confidence}% confidence</div>
                  </div>
                </div>
                <p className="text-sm text-gray-600">{result.reasoning}</p>
              </div>
              <div className="bg-white rounded-xl border border-gray-200 p-4">
                <div className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wider">Matched Policies</div>
                {result.matchedPolicies.map(p => (
                  <div key={p} className="text-sm text-gray-600 py-1 border-b border-gray-100 last:border-0">{p}</div>
                ))}
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center border-2 border-dashed border-gray-200 rounded-xl p-8 text-center">
              <div>
                <Shield className="w-10 h-10 text-gray-700 mx-auto mb-3" />
                <p className="text-sm text-gray-500">Configure a scenario and run the simulation to see how your policies would respond.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
