import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Users, Plus, X, ArrowRight, Mail } from 'lucide-react'
import toast from 'react-hot-toast'

interface Invite { email: string; role: string }

const roles = ['admin', 'manager', 'approver', 'submitter', 'viewer']

export default function TeamSetup() {
  const navigate = useNavigate()
  const [invites, setInvites] = useState<Invite[]>([{ email: '', role: 'manager' }])
  const [loading, setLoading] = useState(false)

  const addRow = () => setInvites(prev => [...prev, { email: '', role: 'submitter' }])
  const removeRow = (i: number) => setInvites(prev => prev.filter((_, idx) => idx !== i))
  const updateRow = (i: number, field: keyof Invite, value: string) => setInvites(prev => prev.map((r, idx) => idx === i ? { ...r, [field]: value } : r))

  const handleSubmit = async () => {
    const valid = invites.filter(i => i.email)
    if (valid.length === 0) { navigate('/onboarding/hindsight'); return }
    setLoading(true)
    await new Promise(r => setTimeout(r, 800))
    toast.success(`${valid.length} invitation(s) sent`)
    navigate('/onboarding/hindsight')
    setLoading(false)
  }

  return (
    <div className="fade-in">
      <div className="mb-8">
        <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center mb-4">
          <Users className="w-6 h-6 text-primary" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Invite your team</h1>
        <p className="text-gray-500">Add team members who will submit, approve, or manage exceptions.</p>
      </div>

      <div className="space-y-2 mb-4">
        {invites.map((invite, i) => (
          <div key={i} className="flex gap-2">
            <div className="relative flex-1">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input type="email" value={invite.email} onChange={e => updateRow(i, 'email', e.target.value)} placeholder="colleague@company.com"
                className="w-full bg-gray-50 border border-gray-200 rounded-lg pl-9 pr-3 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/30 transition-all" />
            </div>
            <select value={invite.role} onChange={e => updateRow(i, 'role', e.target.value)}
              className="bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 focus:outline-none focus:border-primary/60 transition-all">
              {roles.map(r => <option key={r} value={r} className="bg-white capitalize">{r}</option>)}
            </select>
            {invites.length > 1 && (
              <button onClick={() => removeRow(i)} className="p-2.5 rounded-lg bg-gray-50 hover:bg-gray-100 text-gray-500 hover:text-gray-900 transition-colors">
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        ))}
      </div>

      <button onClick={addRow} className="flex items-center gap-2 text-sm text-primary hover:text-primary-dark transition-colors mb-8">
        <Plus className="w-4 h-4" /> Add another
      </button>

      <div className="flex gap-3">
        <button onClick={() => navigate('/onboarding/hindsight')} className="px-6 py-3 rounded-xl bg-gray-100 hover:bg-gray-100 text-gray-900 font-medium text-sm border border-gray-200 transition-colors">
          Skip for now
        </button>
        <button onClick={handleSubmit} disabled={loading} className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold transition-colors disabled:opacity-50">
          {loading && <div className="w-4 h-4 border-2 border-gray-300 border-t-white rounded-full animate-spin" />}
          {loading ? 'Sending...' : (<>Send invitations <ArrowRight className="w-4 h-4" /></>)}
        </button>
      </div>
    </div>
  )
}
