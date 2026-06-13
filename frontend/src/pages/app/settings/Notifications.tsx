import { useState } from 'react'
import { Bell, Save } from 'lucide-react'
import toast from 'react-hot-toast'

const notifGroups = [
  {
    label: 'Exception Activity',
    items: [
      { id: 'exc_submitted', label: 'New exception submitted', desc: 'When someone submits an exception that routes to you' },
      { id: 'exc_approved', label: 'Exception approved', desc: 'When your exception request is approved' },
      { id: 'exc_rejected', label: 'Exception rejected', desc: 'When your exception request is rejected' },
      { id: 'exc_comment', label: 'New comment', desc: 'When someone comments on your exception' },
    ],
  },
  {
    label: 'SLA & Deadlines',
    items: [
      { id: 'sla_warning', label: 'SLA warning', desc: 'When an exception is approaching its deadline' },
      { id: 'sla_missed', label: 'SLA missed', desc: 'When an exception passes its decision deadline' },
    ],
  },
  {
    label: 'AI & Insights',
    items: [
      { id: 'drift_alert', label: 'Policy drift alerts', desc: 'When AI detects unusual exception patterns' },
      { id: 'weekly_digest', label: 'Weekly digest', desc: 'Weekly summary of exception activity and insights' },
    ],
  },
]

export default function Notifications() {
  const [prefs, setPrefs] = useState<Record<string, { email: boolean; inApp: boolean }>>(
    Object.fromEntries(notifGroups.flatMap(g => g.items).map(i => [i.id, { email: true, inApp: true }]))
  )
  const [saving, setSaving] = useState(false)

  const toggle = (id: string, channel: 'email' | 'inApp') => {
    setPrefs(prev => ({ ...prev, [id]: { ...prev[id], [channel]: !prev[id][channel] } }))
  }

  const handleSave = async () => {
    setSaving(true)
    await new Promise(r => setTimeout(r, 800))
    toast.success('Notification preferences saved')
    setSaving(false)
  }

  return (
    <div className="fade-in max-w-2xl">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Bell className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold text-white">Notification Settings</h1>
        </div>
        <button onClick={handleSave} disabled={saving} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-sm font-medium transition-colors disabled:opacity-50">
          {saving ? <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" /> : <Save className="w-4 h-4" />}
          {saving ? 'Saving...' : 'Save'}
        </button>
      </div>

      <div className="space-y-6">
        {notifGroups.map(g => (
          <div key={g.label}>
            <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">{g.label}</h2>
            <div className="bg-dark2 rounded-xl border border-white/10 divide-y divide-white/5">
              <div className="flex items-center gap-4 px-4 py-2 text-xs text-gray-500 font-medium">
                <div className="flex-1" />
                <span className="w-12 text-center">Email</span>
                <span className="w-12 text-center">In-App</span>
              </div>
              {g.items.map(item => (
                <div key={item.id} className="flex items-center gap-4 p-4">
                  <div className="flex-1">
                    <div className="text-sm font-medium text-white">{item.label}</div>
                    <div className="text-xs text-gray-500 mt-0.5">{item.desc}</div>
                  </div>
                  {(['email', 'inApp'] as const).map(ch => (
                    <button key={ch} onClick={() => toggle(item.id, ch)}
                      className={`relative w-9 h-5 rounded-full transition-colors shrink-0 ${prefs[item.id]?.[ch] ? 'bg-primary' : 'bg-white/20'}`}>
                      <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-all ${prefs[item.id]?.[ch] ? 'right-0.5' : 'left-0.5'}`} />
                    </button>
                  ))}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
