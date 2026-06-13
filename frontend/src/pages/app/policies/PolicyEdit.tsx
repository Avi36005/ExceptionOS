import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Save } from 'lucide-react'
import toast from 'react-hot-toast'

export default function PolicyEdit() {
  const { policyId } = useParams()
  const navigate = useNavigate()
  const [content, setContent] = useState(`## Purpose\nThis policy establishes guidelines for the procurement of software tools and licenses across all departments, ensuring security compliance, budget controls, and vendor due diligence.\n\n## Scope\nThis policy applies to all employees, contractors, and vendors who request or procure software on behalf of the organization.\n\n## Policy Statement\nAll software purchases exceeding $1,000 annually must undergo a 30-day procurement review process.`)
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    setSaving(true)
    await new Promise(r => setTimeout(r, 800))
    toast.success('Policy saved as v2.4')
    navigate(`/app/policies/${policyId}`)
  }

  return (
    <div className="fade-in max-w-3xl">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(`/app/policies/${policyId}`)} className="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors">
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-white">Edit Policy</h1>
            <p className="text-sm text-gray-400">{policyId} · Creating v2.4</p>
          </div>
        </div>
        <button onClick={handleSave} disabled={saving} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-sm font-medium transition-colors disabled:opacity-50">
          {saving ? <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" /> : <Save className="w-4 h-4" />}
          {saving ? 'Saving...' : 'Save Version'}
        </button>
      </div>

      <div className="bg-dark2 rounded-xl border border-white/10 overflow-hidden">
        <div className="px-4 py-3 border-b border-white/10 flex items-center gap-2">
          <span className="text-xs font-mono text-gray-500">Markdown</span>
          <span className="w-1 h-1 bg-gray-600 rounded-full" />
          <span className="text-xs text-gray-600">Changes will create a new version</span>
        </div>
        <textarea
          value={content}
          onChange={e => setContent(e.target.value)}
          className="w-full bg-transparent px-6 py-4 text-sm text-gray-200 font-mono focus:outline-none resize-none leading-relaxed"
          rows={30}
        />
      </div>

      <div className="mt-4 p-4 bg-yellow-500/5 border border-yellow-500/20 rounded-xl">
        <p className="text-xs text-yellow-400">Changes will be saved as a new version (v2.4). The previous version (v2.3) will remain accessible in version history. All open exceptions will continue to reference v2.3.</p>
      </div>
    </div>
  )
}
