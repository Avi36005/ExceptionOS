import { useState } from 'react'
import { ArrowLeft, Shield, CheckCircle, Zap } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

export default function OpenClawIntegration() {
  const navigate = useNavigate()
  const [apiKey, setApiKey] = useState('')
  const [enabled, setEnabled] = useState(false)
  const [saving, setSaving] = useState(false)

  const features = [
    'Automatic contract term deviation detection in exceptions',
    'AI-powered NDA clause comparison against policy standards',
    'Risk scoring for vendor legal documents',
    'Automated legal review flagging for high-risk exceptions',
  ]

  const handleSave = async () => {
    if (!apiKey) { toast.error('Please enter your OpenClaw API key'); return }
    setSaving(true)
    await new Promise(r => setTimeout(r, 1000))
    setEnabled(true)
    toast.success('OpenClaw integration connected successfully')
    setSaving(false)
  }

  return (
    <div className="fade-in max-w-2xl">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate('/app/integrations')} className="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div>
          <h1 className="text-xl font-bold text-white">OpenClaw Integration</h1>
          <p className="text-sm text-gray-400">Legal AI document analysis</p>
        </div>
        {enabled && <div className="flex items-center gap-1 text-xs text-green-400 font-medium ml-auto"><CheckCircle className="w-4 h-4" /> Connected</div>}
      </div>

      <div className="bg-dark2 rounded-xl border border-white/10 p-6 mb-4">
        <div className="flex items-center gap-2 mb-4">
          <Shield className="w-5 h-5 text-primary" />
          <h2 className="text-sm font-semibold text-white">What OpenClaw adds to ExceptionOS</h2>
        </div>
        <div className="space-y-3">
          {features.map(f => (
            <div key={f} className="flex items-start gap-2">
              <Zap className="w-4 h-4 text-primary shrink-0 mt-0.5" />
              <p className="text-sm text-gray-300">{f}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-dark2 rounded-xl border border-white/10 p-6">
        <h2 className="text-sm font-semibold text-white mb-4">Configure Connection</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">OpenClaw API Key</label>
            <input type="password" value={apiKey} onChange={e => setApiKey(e.target.value)} placeholder="oc_live_..."
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
            <p className="text-xs text-gray-500 mt-1">Find your API key in the OpenClaw dashboard under Settings → API Keys</p>
          </div>
          <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/10">
            <div>
              <div className="text-sm font-medium text-white">Auto-analyze legal exceptions</div>
              <div className="text-xs text-gray-500">Automatically run OpenClaw analysis on Legal category exceptions</div>
            </div>
            <button onClick={() => {}} className="relative w-10 h-5 rounded-full bg-primary flex items-center">
              <div className="absolute right-0.5 w-4 h-4 bg-white rounded-full shadow" />
            </button>
          </div>
          <button onClick={handleSave} disabled={saving}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold transition-colors disabled:opacity-50">
            {saving && <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />}
            {saving ? 'Connecting...' : 'Connect OpenClaw'}
          </button>
        </div>
      </div>
    </div>
  )
}
