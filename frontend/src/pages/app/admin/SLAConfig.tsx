import { Clock, Save } from 'lucide-react'
import { useState } from 'react'
import toast from 'react-hot-toast'

const categories = ['IT & Security', 'HR & Employment', 'Vendor & Procurement', 'Finance & Compliance', 'Legal & Contracts', 'Operations']
const priorities = ['low', 'medium', 'high', 'critical']

const defaultSLAs: Record<string, Record<string, number>> = {
  'IT & Security': { low: 120, medium: 48, high: 24, critical: 4 },
  'HR & Employment': { low: 168, medium: 72, high: 48, critical: 24 },
  'Vendor & Procurement': { low: 120, medium: 72, high: 48, critical: 24 },
  'Finance & Compliance': { low: 96, medium: 48, high: 24, critical: 8 },
  'Legal & Contracts': { low: 168, medium: 96, high: 48, critical: 24 },
  'Operations': { low: 120, medium: 48, high: 24, critical: 8 },
}

export default function SLAConfig() {
  const [slas, setSlas] = useState(defaultSLAs)
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    setSaving(true)
    await new Promise(r => setTimeout(r, 800))
    toast.success('SLA configuration saved')
    setSaving(false)
  }

  const update = (category: string, priority: string, value: number) => {
    setSlas(prev => ({ ...prev, [category]: { ...prev[category], [priority]: value } }))
  }

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Clock className="w-6 h-6 text-primary" />
          <div>
            <h1 className="text-2xl font-bold text-white">SLA Configuration</h1>
            <p className="text-sm text-gray-400 mt-1">Set decision deadlines by category and priority (in hours).</p>
          </div>
        </div>
        <button onClick={handleSave} disabled={saving} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-sm font-medium transition-colors disabled:opacity-50">
          {saving ? <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" /> : <Save className="w-4 h-4" />}
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      <div className="bg-dark2 rounded-xl border border-white/10 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Category</th>
              {priorities.map(p => (
                <th key={p} className="text-center py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider capitalize">{p}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {categories.map(cat => (
              <tr key={cat} className="border-b border-white/5">
                <td className="py-3 px-4 text-gray-300 font-medium">{cat}</td>
                {priorities.map(p => (
                  <td key={p} className="py-3 px-4 text-center">
                    <div className="flex items-center justify-center gap-1">
                      <input
                        type="number"
                        value={slas[cat]?.[p] || ''}
                        onChange={e => update(cat, p, Number(e.target.value))}
                        className="w-16 bg-white/5 border border-white/10 rounded px-2 py-1 text-sm text-white text-center focus:outline-none focus:border-primary/60 transition-all"
                      />
                      <span className="text-xs text-gray-600">h</span>
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
