import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Building2, ArrowRight } from 'lucide-react'
import { useOrgStore } from '../../store/orgStore'
import toast from 'react-hot-toast'

const industries = ['Technology', 'Finance', 'Healthcare', 'Legal', 'Manufacturing', 'Retail', 'Education', 'Government', 'Other']
const sizes = ['1-10', '11-50', '51-200', '201-500', '500+']

export default function CompanySetup() {
  const navigate = useNavigate()
  const { setCurrentOrg, setUserRole } = useOrgStore()
  const [form, setForm] = useState({ name: '', slug: '', industry: '', size: '' })
  const [loading, setLoading] = useState(false)

  const handleNameChange = (name: string) => {
    setForm(prev => ({ ...prev, name, slug: name.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '') }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.name || !form.industry || !form.size) { toast.error('Please fill all fields'); return }
    setLoading(true)
    await new Promise(r => setTimeout(r, 800))
    setCurrentOrg({ id: '1', name: form.name, slug: form.slug, plan: 'trial', hindsightEnabled: false, demoMode: false })
    setUserRole('owner')
    setLoading(false)
    navigate('/onboarding/policies')
  }

  return (
    <div className="fade-in">
      <div className="mb-8">
        <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center mb-4">
          <Building2 className="w-6 h-6 text-primary" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Set up your organization</h1>
        <p className="text-gray-500">Tell us about your company so we can configure ExceptionOS for you.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1.5">Organization name</label>
          <input type="text" value={form.name} onChange={e => handleNameChange(e.target.value)} placeholder="Acme Corporation" required
            className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/30 transition-all" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1.5">Unique slug (URL identifier)</label>
          <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5">
            <span className="text-gray-500 text-sm">app.exceptionos.io/</span>
            <input type="text" value={form.slug} onChange={e => setForm(p => ({ ...p, slug: e.target.value }))} placeholder="acme" required
              className="flex-1 bg-transparent text-sm text-gray-900 placeholder-gray-500 focus:outline-none" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1.5">Industry</label>
          <select value={form.industry} onChange={e => setForm(p => ({ ...p, industry: e.target.value }))} required
            className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/30 transition-all">
            <option value="">Select industry</option>
            {industries.map(i => <option key={i} value={i} className="bg-white">{i}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1.5">Organization size</label>
          <div className="grid grid-cols-5 gap-2">
            {sizes.map(s => (
              <button key={s} type="button" onClick={() => setForm(p => ({ ...p, size: s }))}
                className={`py-2 rounded-lg text-sm font-medium border transition-all ${form.size === s ? 'bg-primary/20 border-primary/50 text-primary' : 'bg-gray-50 border-gray-200 text-gray-500 hover:border-gray-300'}`}>
                {s}
              </button>
            ))}
          </div>
        </div>

        <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold transition-colors disabled:opacity-50 mt-4">
          {loading && <div className="w-4 h-4 border-2 border-gray-300 border-t-white rounded-full animate-spin" />}
          {loading ? 'Saving...' : (<>Continue <ArrowRight className="w-4 h-4" /></>)}
        </button>
      </form>
    </div>
  )
}
