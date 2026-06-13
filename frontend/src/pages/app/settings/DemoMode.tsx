import { useState } from 'react'
import { Zap, Play, RefreshCw } from 'lucide-react'
import { useOrgStore } from '../../../store/orgStore'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

export default function DemoMode() {
  const { currentOrg, setCurrentOrg } = useOrgStore()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const enabled = currentOrg?.demoMode || false

  const toggleDemo = async () => {
    setLoading(true)
    await new Promise(r => setTimeout(r, 800))
    if (currentOrg) setCurrentOrg({ ...currentOrg, demoMode: !enabled })
    toast.success(enabled ? 'Demo mode disabled' : 'Demo mode enabled — synthetic data loaded')
    setLoading(false)
  }

  return (
    <div className="fade-in max-w-xl">
      <div className="flex items-center gap-3 mb-6">
        <Zap className="w-6 h-6 text-primary" />
        <h1 className="text-2xl font-bold text-white">Demo Mode</h1>
      </div>

      <div className="bg-dark2 rounded-xl border border-white/10 p-6 mb-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-semibold text-white mb-1">Enable Demo Mode</h2>
            <p className="text-xs text-gray-400">Load synthetic data to showcase ExceptionOS to stakeholders without using real organizational data.</p>
          </div>
          <button onClick={toggleDemo} disabled={loading}
            className={`relative w-11 h-6 rounded-full transition-colors ${enabled ? 'bg-primary' : 'bg-white/20'}`}>
            <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${enabled ? 'translate-x-5' : ''}`} />
          </button>
        </div>

        {enabled && (
          <div className="p-3 bg-primary/5 border border-primary/20 rounded-lg fade-in">
            <div className="text-xs font-semibold text-primary mb-1">Demo Mode Active</div>
            <p className="text-xs text-gray-400">48 synthetic exceptions, 15 policies, and 84 precedents have been loaded. This data is completely fictional and will not affect your organization's real data.</p>
          </div>
        )}
      </div>

      {enabled && (
        <div className="space-y-3 fade-in">
          <button onClick={() => navigate('/demo/story')} className="w-full flex items-center gap-3 p-4 bg-dark2 rounded-xl border border-white/10 hover:border-primary/30 transition-all text-left">
            <Play className="w-5 h-5 text-primary shrink-0" />
            <div>
              <div className="text-sm font-semibold text-white">Launch Demo Story</div>
              <div className="text-xs text-gray-400">Guided walkthrough of ExceptionOS features</div>
            </div>
          </button>
          <button onClick={() => navigate('/demo/hindsight-live')} className="w-full flex items-center gap-3 p-4 bg-dark2 rounded-xl border border-white/10 hover:border-primary/30 transition-all text-left">
            <Zap className="w-5 h-5 text-primary shrink-0" />
            <div>
              <div className="text-sm font-semibold text-white">Hindsight™ Live Demo</div>
              <div className="text-xs text-gray-400">See AI memory in action in real-time</div>
            </div>
          </button>
          <button onClick={toggleDemo} disabled={loading} className="w-full flex items-center gap-3 p-4 bg-dark2 rounded-xl border border-white/10 hover:border-red-500/20 transition-all text-left">
            <RefreshCw className="w-5 h-5 text-red-400 shrink-0" />
            <div>
              <div className="text-sm font-semibold text-red-400">Reset Demo Data</div>
              <div className="text-xs text-gray-400">Clear all demo data and return to your real data</div>
            </div>
          </button>
        </div>
      )}
    </div>
  )
}
