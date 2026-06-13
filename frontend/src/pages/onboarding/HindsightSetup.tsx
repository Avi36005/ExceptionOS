import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Brain, Check, ArrowRight, Sparkles } from 'lucide-react'
import { useOrgStore } from '../../store/orgStore'

const features = [
  'AI analyzes every exception against past decisions',
  'Flags patterns of policy drift and exception clustering',
  'Generates consistency scores for approvers',
  'Provides natural-language memory queries',
  'Automatic precedent tagging and cross-referencing',
]

export default function HindsightSetup() {
  const navigate = useNavigate()
  const { currentOrg, setCurrentOrg } = useOrgStore()
  const [enabled, setEnabled] = useState(true)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    setLoading(true)
    await new Promise(r => setTimeout(r, 1000))
    if (currentOrg) {
      setCurrentOrg({ ...currentOrg, hindsightEnabled: enabled })
    }
    navigate('/app')
    setLoading(false)
  }

  return (
    <div className="fade-in">
      <div className="mb-8">
        <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center mb-4">
          <Brain className="w-6 h-6 text-primary" />
        </div>
        <div className="flex items-center gap-2 mb-2">
          <h1 className="text-2xl font-bold text-white">Enable Hindsight™</h1>
          <span className="px-2 py-0.5 rounded-full bg-primary/20 text-primary text-xs font-semibold">AI Feature</span>
        </div>
        <p className="text-gray-400">Hindsight™ is ExceptionOS's institutional memory engine. It learns from every decision your organization makes.</p>
      </div>

      {/* Feature list */}
      <div className="bg-primary/5 border border-primary/20 rounded-xl p-5 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-4 h-4 text-primary" />
          <span className="text-sm font-semibold text-white">What Hindsight™ does</span>
        </div>
        <div className="space-y-3">
          {features.map(f => (
            <div key={f} className="flex items-start gap-2">
              <Check className="w-4 h-4 text-primary shrink-0 mt-0.5" />
              <span className="text-sm text-gray-300">{f}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Toggle */}
      <div className="flex items-center justify-between p-4 bg-white/5 border border-white/10 rounded-xl mb-8">
        <div>
          <div className="text-sm font-medium text-white">Enable Hindsight™ Memory Engine</div>
          <div className="text-xs text-gray-500 mt-0.5">You can change this later in organization settings</div>
        </div>
        <button
          onClick={() => setEnabled(!enabled)}
          className={`relative w-11 h-6 rounded-full transition-colors ${enabled ? 'bg-primary' : 'bg-white/20'}`}
        >
          <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${enabled ? 'translate-x-5' : ''}`} />
        </button>
      </div>

      <button onClick={handleSubmit} disabled={loading} className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold transition-colors disabled:opacity-50">
        {loading && <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />}
        {loading ? 'Setting up...' : (<>Launch ExceptionOS <ArrowRight className="w-4 h-4" /></>)}
      </button>
    </div>
  )
}
