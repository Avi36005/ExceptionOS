import { useState } from 'react'
import { CheckCircle, XCircle, ArrowUpCircle, MessageSquare } from 'lucide-react'
import toast from 'react-hot-toast'
import { useNavigate, useParams } from 'react-router-dom'

const decisions = [
  { id: 'approved', label: 'Approve', icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-500/10 border-green-500/30 hover:bg-green-500/20' },
  { id: 'rejected', label: 'Reject', icon: XCircle, color: 'text-red-600', bg: 'bg-red-500/10 border-red-500/30 hover:bg-red-500/20' },
  { id: 'escalated', label: 'Escalate', icon: ArrowUpCircle, color: 'text-orange-600', bg: 'bg-orange-500/10 border-orange-500/30 hover:bg-orange-500/20' },
]

export default function ExceptionDecision() {
  const navigate = useNavigate()
  const { caseId } = useParams()
  const [decision, setDecision] = useState('')
  const [rationale, setRationale] = useState('')
  const [conditions, setConditions] = useState('CISO security sign-off required within 24 hours\nLicense limited to 90 days\nFull procurement to be completed in parallel')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!decision || !rationale) { toast.error('Please select a decision and provide rationale'); return }
    setLoading(true)
    await new Promise(r => setTimeout(r, 1200))
    toast.success(`Exception ${decision} successfully`)
    navigate(`/app/exceptions/${caseId}/outcome`)
  }

  return (
    <div className="fade-in space-y-6 max-w-2xl">
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Your Decision</h3>
        <div className="grid grid-cols-3 gap-3">
          {decisions.map(d => (
            <button key={d.id} onClick={() => setDecision(d.id)}
              className={`flex flex-col items-center gap-2 p-4 rounded-xl border transition-all ${decision === d.id ? d.bg + ' ring-1 ring-offset-1 ring-offset-white ring-primary' : 'bg-gray-50 border-gray-200 hover:border-gray-300'}`}>
              <d.icon className={`w-6 h-6 ${d.color}`} />
              <span className="text-sm font-semibold text-gray-900">{d.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <label className="block text-sm font-medium text-gray-600 mb-2">
          <div className="flex items-center gap-2"><MessageSquare className="w-4 h-4 text-gray-500" />Decision Rationale *</div>
        </label>
        <textarea value={rationale} onChange={e => setRationale(e.target.value)}
          placeholder="Explain your decision. This will be part of the permanent audit trail and will be used to inform future similar decisions..."
          rows={5}
          className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/30 transition-all resize-none" />
      </div>

      {decision === 'approved' && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 fade-in">
          <label className="block text-sm font-medium text-gray-600 mb-2">Conditions & Limitations (optional)</label>
          <textarea value={conditions} onChange={e => setConditions(e.target.value)}
            rows={4}
            className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/30 transition-all resize-none" />
          <p className="text-xs text-gray-500 mt-2">These conditions will be tracked and the requester will be notified</p>
        </div>
      )}

      <div className="flex items-center gap-3 p-4 bg-gray-50 border border-gray-200 rounded-xl">
        <div className="w-4 h-4 rounded border border-primary shrink-0 flex items-center justify-center">
          <div className="w-2 h-2 bg-primary rounded-sm" />
        </div>
        <p className="text-xs text-gray-500">I confirm this decision is based on my review of all available evidence, policies, and precedents. This decision will be permanently recorded.</p>
      </div>

      <button onClick={handleSubmit} disabled={loading || !decision || !rationale}
        className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold transition-colors disabled:opacity-50">
        {loading && <div className="w-4 h-4 border-2 border-gray-300 border-t-white rounded-full animate-spin" />}
        {loading ? 'Recording decision...' : 'Submit Decision'}
      </button>
    </div>
  )
}
