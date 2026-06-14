import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BookOpen, ArrowRight, Check } from 'lucide-react'

const templates = [
  { id: 'vendor', name: 'Vendor & Procurement', desc: 'NDA exceptions, budget overrides, sole-source justifications', count: 12 },
  { id: 'hr', name: 'HR & Employment', desc: 'Hiring exceptions, compensation deviations, leave policy', count: 8 },
  { id: 'it', name: 'IT & Security', desc: 'Software approvals, access control exceptions, BYOD policy', count: 15 },
  { id: 'finance', name: 'Finance & Compliance', desc: 'Expense approvals, budget transfers, audit exceptions', count: 10 },
  { id: 'legal', name: 'Legal & Contracts', desc: 'Contract term deviations, liability caps, IP exceptions', count: 9 },
]

export default function PoliciesSetup() {
  const navigate = useNavigate()
  const [selected, setSelected] = useState<string[]>(['vendor', 'hr'])
  const [loading, setLoading] = useState(false)

  const toggle = (id: string) => setSelected(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])

  const handleSubmit = async () => {
    setLoading(true)
    await new Promise(r => setTimeout(r, 800))
    setLoading(false)
    navigate('/onboarding/team')
  }

  return (
    <div className="fade-in">
      <div className="mb-8">
        <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center mb-4">
          <BookOpen className="w-6 h-6 text-primary" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Import policy templates</h1>
        <p className="text-gray-500">Start with curated policy templates for your industry. You can customize everything later.</p>
      </div>

      <div className="space-y-3 mb-6">
        {templates.map(t => (
          <button key={t.id} onClick={() => toggle(t.id)}
            className={`w-full flex items-center gap-4 p-4 rounded-xl border transition-all text-left ${selected.includes(t.id) ? 'bg-primary/10 border-primary/40' : 'bg-gray-50 border-gray-200 hover:border-gray-300'}`}>
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${selected.includes(t.id) ? 'bg-primary' : 'bg-gray-100'}`}>
              {selected.includes(t.id) ? <Check className="w-4 h-4 text-white" /> : <BookOpen className="w-4 h-4 text-gray-500" />}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-900">{t.name}</div>
              <div className="text-xs text-gray-500 mt-0.5">{t.desc}</div>
            </div>
            <span className="text-xs text-gray-500 shrink-0">{t.count} policies</span>
          </button>
        ))}
      </div>

      <p className="text-xs text-gray-500 mb-6">{selected.length} template sets selected · {selected.reduce((a, id) => a + (templates.find(t => t.id === id)?.count ?? 0), 0)} policies will be imported</p>

      <button onClick={handleSubmit} disabled={loading} className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold transition-colors disabled:opacity-50">
        {loading && <div className="w-4 h-4 border-2 border-gray-300 border-t-white rounded-full animate-spin" />}
        {loading ? 'Importing...' : (<>Continue <ArrowRight className="w-4 h-4" /></>)}
      </button>
    </div>
  )
}
