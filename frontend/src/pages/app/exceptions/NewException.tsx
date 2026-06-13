import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, ArrowRight, FileText, Sparkles } from 'lucide-react'
import toast from 'react-hot-toast'

const categories = ['IT & Security', 'HR & Employment', 'Vendor & Procurement', 'Finance & Compliance', 'Legal & Contracts', 'Operations', 'Other']
const priorities = ['low', 'medium', 'high', 'critical']

export default function NewException() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [aiLoading, setAiLoading] = useState(false)
  const [form, setForm] = useState({
    title: '',
    category: '',
    priority: 'medium',
    policyId: '',
    description: '',
    businessJustification: '',
    requestedBy: '',
    department: '',
    amount: '',
    deadline: '',
  })

  const handleAiSuggest = async () => {
    if (!form.description) { toast.error('Please enter a description first'); return }
    setAiLoading(true)
    await new Promise(r => setTimeout(r, 1500))
    setForm(prev => ({
      ...prev,
      title: 'Emergency software license exception for design team productivity',
      category: 'IT & Security',
      priority: 'high',
      businessJustification: 'The design team requires immediate access to advanced prototyping tools to meet the Q1 product launch deadline. Current policy requires a 30-day procurement process, but the project timeline allows only 5 days. Estimated business impact of delay: $120,000 in delayed revenue.',
    }))
    setAiLoading(false)
    toast.success('AI filled in the form based on your description')
  }

  const handleSubmit = async () => {
    if (!form.title || !form.category || !form.description) { toast.error('Please fill in all required fields'); return }
    setLoading(true)
    await new Promise(r => setTimeout(r, 1200))
    toast.success('Exception submitted successfully')
    navigate('/app/exceptions/EXC-1049/intake')
  }

  const update = (field: string, value: string) => setForm(prev => ({ ...prev, [field]: value }))

  return (
    <div className="fade-in max-w-2xl">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate(-1)} className="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div>
          <h1 className="text-xl font-bold text-white">New Exception Request</h1>
          <p className="text-sm text-gray-400">Step {step} of 2</p>
        </div>
      </div>

      {/* Progress */}
      <div className="flex gap-2 mb-8">
        {[1, 2].map(s => (
          <div key={s} className={`h-1 flex-1 rounded-full transition-all ${s <= step ? 'bg-primary' : 'bg-white/10'}`} />
        ))}
      </div>

      {step === 1 && (
        <div className="space-y-5 fade-in">
          <div className="bg-primary/5 border border-primary/20 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <Sparkles className="w-5 h-5 text-primary shrink-0 mt-0.5" />
              <div className="flex-1">
                <div className="text-sm font-medium text-white mb-2">Start with AI assist</div>
                <textarea value={form.description} onChange={e => update('description', e.target.value)}
                  placeholder="Describe your exception request in plain language. AI will help structure the rest of the form..."
                  rows={3}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all resize-none mb-3" />
                <button onClick={handleAiSuggest} disabled={aiLoading}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white font-medium text-sm transition-colors disabled:opacity-50">
                  {aiLoading ? <div className="w-3 h-3 border-2 border-white/20 border-t-white rounded-full animate-spin" /> : <Sparkles className="w-3 h-3" />}
                  {aiLoading ? 'Analyzing...' : 'Auto-fill with AI'}
                </button>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Exception Title *</label>
            <input type="text" value={form.title} onChange={e => update('title', e.target.value)} placeholder="Concise description of what you're requesting an exception for"
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/30 transition-all" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Category *</label>
              <select value={form.category} onChange={e => update('category', e.target.value)}
                className="w-full appearance-none bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-primary/60 transition-all">
                <option value="">Select category</option>
                {categories.map(c => <option key={c} value={c} className="bg-dark2">{c}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Priority</label>
              <div className="grid grid-cols-4 gap-1">
                {priorities.map(p => (
                  <button key={p} type="button" onClick={() => update('priority', p)}
                    className={`py-2 rounded-lg text-xs font-medium capitalize border transition-all ${form.priority === p ? 'bg-primary/20 border-primary/50 text-primary' : 'bg-white/5 border-white/10 text-gray-400 hover:border-white/20'}`}>
                    {p}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Department</label>
              <input type="text" value={form.department} onChange={e => update('department', e.target.value)} placeholder="e.g. Engineering"
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Requested By</label>
              <input type="text" value={form.requestedBy} onChange={e => update('requestedBy', e.target.value)} placeholder="Your name"
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
            </div>
          </div>

          <button onClick={() => setStep(2)} disabled={!form.title || !form.category}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold transition-colors disabled:opacity-50">
            Continue <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-5 fade-in">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Business Justification *</label>
            <textarea value={form.businessJustification} onChange={e => update('businessJustification', e.target.value)}
              placeholder="Why is this exception necessary? What business impact would occur without it?"
              rows={5}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/30 transition-all resize-none" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Financial Amount (if applicable)</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">$</span>
                <input type="number" value={form.amount} onChange={e => update('amount', e.target.value)} placeholder="0.00"
                  className="w-full bg-white/5 border border-white/10 rounded-lg pl-7 pr-3 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Decision Needed By</label>
              <input type="date" value={form.deadline} onChange={e => update('deadline', e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-primary/60 transition-all" />
            </div>
          </div>

          <div className="p-4 bg-white/5 border border-white/10 rounded-xl">
            <div className="flex items-center gap-2 mb-3">
              <FileText className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium text-white">Attach Evidence</span>
            </div>
            <div className="border-2 border-dashed border-white/10 rounded-lg p-6 text-center hover:border-primary/30 transition-colors cursor-pointer">
              <p className="text-sm text-gray-400">Drop files here or click to upload</p>
              <p className="text-xs text-gray-600 mt-1">PDF, DOC, XLS, PNG up to 10MB each</p>
            </div>
          </div>

          <div className="flex gap-3">
            <button onClick={() => setStep(1)} className="px-6 py-3 rounded-xl bg-white/10 hover:bg-white/15 text-white font-medium text-sm border border-white/10 transition-colors">
              Back
            </button>
            <button onClick={handleSubmit} disabled={loading || !form.businessJustification}
              className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold transition-colors disabled:opacity-50">
              {loading && <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />}
              {loading ? 'Submitting...' : 'Submit Exception'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
