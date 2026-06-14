import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, BookOpen, Sparkles } from 'lucide-react'
import toast from 'react-hot-toast'

const categories = ['IT & Security', 'HR & Employment', 'Vendor & Procurement', 'Finance & Compliance', 'Legal & Contracts', 'Operations']

export default function NewPolicy() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ title: '', category: '', description: '', content: '', effectiveDate: '', reviewDate: '', owner: '' })
  const [loading, setLoading] = useState(false)
  const [aiLoading, setAiLoading] = useState(false)

  const handleAi = async () => {
    if (!form.title || !form.category) { toast.error('Please enter a title and category first'); return }
    setAiLoading(true)
    await new Promise(r => setTimeout(r, 2000))
    setForm(prev => ({ ...prev, content: `## Purpose\nThis policy establishes guidelines for ${form.title.toLowerCase()}.\n\n## Scope\nThis policy applies to all employees and contractors.\n\n## Policy Statement\n[AI-generated policy content based on "${form.title}" in ${form.category}]\n\n## Exception Process\nRequests for exceptions to this policy must be submitted through ExceptionOS with appropriate business justification.\n\n## Review Cycle\nThis policy will be reviewed annually or when significant changes occur.` }))
    setAiLoading(false)
    toast.success('AI drafted the policy content')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.title || !form.category || !form.content) { toast.error('Please fill all required fields'); return }
    setLoading(true)
    await new Promise(r => setTimeout(r, 1000))
    toast.success('Policy created successfully')
    navigate('/app/policies')
  }

  const update = (field: string, value: string) => setForm(prev => ({ ...prev, [field]: value }))

  return (
    <div className="fade-in max-w-2xl">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate('/app/policies')} className="p-2 rounded-lg hover:bg-gray-50 text-gray-500 hover:text-gray-900 transition-colors">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-primary" />
          <h1 className="text-xl font-bold text-gray-900">New Policy</h1>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1.5">Policy Title *</label>
          <input type="text" value={form.title} onChange={e => update('title', e.target.value)} placeholder="e.g. Software Procurement Policy"
            className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">Category *</label>
            <select value={form.category} onChange={e => update('category', e.target.value)}
              className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 focus:outline-none focus:border-primary/60 transition-all">
              <option value="">Select category</option>
              {categories.map(c => <option key={c} value={c} className="bg-white">{c}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">Policy Owner</label>
            <input type="text" value={form.owner} onChange={e => update('owner', e.target.value)} placeholder="e.g. CTO Office"
              className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">Effective Date</label>
            <input type="date" value={form.effectiveDate} onChange={e => update('effectiveDate', e.target.value)}
              className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 focus:outline-none focus:border-primary/60 transition-all" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">Review Date</label>
            <input type="date" value={form.reviewDate} onChange={e => update('reviewDate', e.target.value)}
              className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 focus:outline-none focus:border-primary/60 transition-all" />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="block text-sm font-medium text-gray-600">Policy Content *</label>
            <button type="button" onClick={handleAi} disabled={aiLoading}
              className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-primary/10 hover:bg-primary/20 text-primary text-xs font-medium transition-colors disabled:opacity-50">
              {aiLoading ? <div className="w-3 h-3 border-2 border-primary/30 border-t-primary rounded-full animate-spin" /> : <Sparkles className="w-3 h-3" />}
              {aiLoading ? 'Drafting...' : 'AI Draft'}
            </button>
          </div>
          <textarea value={form.content} onChange={e => update('content', e.target.value)} placeholder="Write policy content in Markdown format..."
            rows={10}
            className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/30 transition-all resize-none font-mono" />
        </div>

        <div className="flex gap-3">
          <button type="button" onClick={() => navigate('/app/policies')} className="px-6 py-3 rounded-xl bg-gray-100 hover:bg-gray-100 text-gray-900 font-medium text-sm border border-gray-200 transition-colors">
            Cancel
          </button>
          <button type="submit" disabled={loading} className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold transition-colors disabled:opacity-50">
            {loading && <div className="w-4 h-4 border-2 border-gray-300 border-t-white rounded-full animate-spin" />}
            {loading ? 'Creating...' : 'Create Policy'}
          </button>
        </div>
      </form>
    </div>
  )
}
