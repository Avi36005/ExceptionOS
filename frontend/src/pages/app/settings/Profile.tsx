import { useState } from 'react'
import { User, Save, Camera } from 'lucide-react'
import { useAuthStore } from '../../../store/authStore'
import toast from 'react-hot-toast'

export default function Profile() {
  const { user } = useAuthStore()
  const [form, setForm] = useState({
    fullName: user?.user_metadata?.full_name || '',
    email: user?.email || '',
    jobTitle: 'Operations Manager',
    department: 'Operations',
    phone: '+1 (555) 000-0000',
  })
  const [saving, setSaving] = useState(false)

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    await new Promise(r => setTimeout(r, 800))
    toast.success('Profile updated')
    setSaving(false)
  }

  return (
    <div className="fade-in max-w-xl">
      <div className="flex items-center gap-3 mb-6">
        <User className="w-6 h-6 text-primary" />
        <h1 className="text-2xl font-bold text-gray-900">Profile Settings</h1>
      </div>

      {/* Avatar */}
      <div className="flex items-center gap-4 mb-8">
        <div className="relative">
          <div className="w-20 h-20 rounded-2xl bg-primary/20 flex items-center justify-center text-3xl font-bold text-primary">
            {form.fullName?.[0]?.toUpperCase() || 'U'}
          </div>
          <button className="absolute -bottom-1 -right-1 w-7 h-7 rounded-full bg-primary flex items-center justify-center">
            <Camera className="w-3.5 h-3.5 text-white" />
          </button>
        </div>
        <div>
          <div className="text-sm font-semibold text-gray-900">{form.fullName || 'User'}</div>
          <div className="text-xs text-gray-500">{form.email}</div>
          <button className="text-xs text-primary hover:text-primary-dark transition-colors mt-1">Change avatar</button>
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">Full Name</label>
            <input type="text" value={form.fullName} onChange={e => setForm(p => ({ ...p, fullName: e.target.value }))}
              className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">Email</label>
            <input type="email" value={form.email} disabled
              className="w-full bg-gray-50 border border-gray-100 rounded-lg px-3 py-2.5 text-sm text-gray-500 cursor-not-allowed" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">Job Title</label>
            <input type="text" value={form.jobTitle} onChange={e => setForm(p => ({ ...p, jobTitle: e.target.value }))}
              className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">Department</label>
            <input type="text" value={form.department} onChange={e => setForm(p => ({ ...p, department: e.target.value }))}
              className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1.5">Phone</label>
          <input type="tel" value={form.phone} onChange={e => setForm(p => ({ ...p, phone: e.target.value }))}
            className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
        </div>
        <button type="submit" disabled={saving} className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-primary hover:bg-primary-dark text-white font-medium text-sm transition-colors disabled:opacity-50">
          {saving ? <div className="w-4 h-4 border-2 border-gray-300 border-t-white rounded-full animate-spin" /> : <Save className="w-4 h-4" />}
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </form>
    </div>
  )
}
