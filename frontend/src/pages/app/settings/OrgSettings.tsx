import { useState } from 'react'
import { Building2, Save } from 'lucide-react'
import { useOrgStore } from '../../../store/orgStore'
import toast from 'react-hot-toast'

export default function OrgSettings() {
  const { currentOrg } = useOrgStore()
  const [form, setForm] = useState({
    name: currentOrg?.name || '',
    slug: currentOrg?.slug || '',
    website: '',
    timezone: 'America/New_York',
    retentionDays: '2555',
  })
  const [saving, setSaving] = useState(false)

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    await new Promise(r => setTimeout(r, 800))
    toast.success('Organization settings updated')
    setSaving(false)
  }

  return (
    <div className="fade-in max-w-xl">
      <div className="flex items-center gap-3 mb-6">
        <Building2 className="w-6 h-6 text-primary" />
        <h1 className="text-2xl font-bold text-gray-900">Organization Settings</h1>
      </div>

      <form onSubmit={handleSave} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1.5">Organization Name</label>
          <input type="text" value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
            className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1.5">Organization Slug</label>
          <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5">
            <span className="text-gray-500 text-sm">app.exceptionos.io/</span>
            <input type="text" value={form.slug} onChange={e => setForm(p => ({ ...p, slug: e.target.value }))}
              className="flex-1 bg-transparent text-sm text-gray-900 focus:outline-none" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1.5">Website</label>
          <input type="url" value={form.website} onChange={e => setForm(p => ({ ...p, website: e.target.value }))} placeholder="https://yourcompany.com"
            className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">Timezone</label>
            <select value={form.timezone} onChange={e => setForm(p => ({ ...p, timezone: e.target.value }))}
              className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 focus:outline-none focus:border-primary/60 transition-all">
              <option value="America/New_York">Eastern (ET)</option>
              <option value="America/Chicago">Central (CT)</option>
              <option value="America/Denver">Mountain (MT)</option>
              <option value="America/Los_Angeles">Pacific (PT)</option>
              <option value="UTC">UTC</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">Data Retention (days)</label>
            <input type="number" value={form.retentionDays} onChange={e => setForm(p => ({ ...p, retentionDays: e.target.value }))}
              className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-900 focus:outline-none focus:border-primary/60 transition-all" />
          </div>
        </div>
        <button type="submit" disabled={saving} className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-primary hover:bg-primary-dark text-white font-medium text-sm transition-colors disabled:opacity-50">
          {saving ? <div className="w-4 h-4 border-2 border-gray-300 border-t-white rounded-full animate-spin" /> : <Save className="w-4 h-4" />}
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </form>
    </div>
  )
}
