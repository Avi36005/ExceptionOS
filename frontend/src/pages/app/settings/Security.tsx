import { useState } from 'react'
import { Shield, Lock, LogOut } from 'lucide-react'
import { updatePassword } from '../../../lib/auth'
import toast from 'react-hot-toast'

export default function Security() {
  const [pwForm, setPwForm] = useState({ current: '', new: '', confirm: '' })
  const [pwLoading, setPwLoading] = useState(false)
  const [mfaEnabled, setMfaEnabled] = useState(false)

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    if (pwForm.new !== pwForm.confirm) { toast.error('Passwords do not match'); return }
    if (pwForm.new.length < 8) { toast.error('Password must be at least 8 characters'); return }
    setPwLoading(true)
    try {
      await updatePassword(pwForm.new)
      toast.success('Password updated successfully')
      setPwForm({ current: '', new: '', confirm: '' })
    } catch { toast.error('Failed to update password') }
    setPwLoading(false)
  }

  return (
    <div className="fade-in max-w-xl space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Shield className="w-6 h-6 text-primary" />
        <h1 className="text-2xl font-bold text-white">Security Settings</h1>
      </div>

      {/* Password */}
      <div className="bg-dark2 rounded-xl border border-white/10 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Lock className="w-4 h-4 text-gray-500" />
          <h2 className="text-sm font-semibold text-white">Change Password</h2>
        </div>
        <form onSubmit={handleChangePassword} className="space-y-3">
          {[
            { label: 'Current password', field: 'current' as const },
            { label: 'New password', field: 'new' as const },
            { label: 'Confirm new password', field: 'confirm' as const },
          ].map(f => (
            <div key={f.field}>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">{f.label}</label>
              <input type="password" value={pwForm[f.field]} onChange={e => setPwForm(p => ({ ...p, [f.field]: e.target.value }))}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
            </div>
          ))}
          <button type="submit" disabled={pwLoading} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-sm font-medium transition-colors disabled:opacity-50 mt-2">
            {pwLoading && <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />}
            {pwLoading ? 'Updating...' : 'Update Password'}
          </button>
        </form>
      </div>

      {/* MFA */}
      <div className="bg-dark2 rounded-xl border border-white/10 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-white mb-1">Two-Factor Authentication</h2>
            <p className="text-xs text-gray-400">Add an extra layer of security to your account.</p>
          </div>
          <button onClick={() => { setMfaEnabled(!mfaEnabled); toast.success(mfaEnabled ? '2FA disabled' : '2FA enabled') }}
            className={`relative w-11 h-6 rounded-full transition-colors ${mfaEnabled ? 'bg-primary' : 'bg-white/20'}`}>
            <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${mfaEnabled ? 'translate-x-5' : ''}`} />
          </button>
        </div>
      </div>

      {/* Sessions */}
      <div className="bg-dark2 rounded-xl border border-white/10 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-white">Active Sessions</h2>
          <button className="flex items-center gap-1 text-xs text-red-400 hover:text-red-300 transition-colors">
            <LogOut className="w-3 h-3" /> Sign out all
          </button>
        </div>
        {[
          { device: 'Chrome on macOS', location: 'New York, US', current: true, time: 'Active now' },
          { device: 'Safari on iPhone', location: 'New York, US', current: false, time: '2 days ago' },
        ].map((s, i) => (
          <div key={i} className="flex items-center justify-between py-3 border-b border-white/5 last:border-0">
            <div>
              <div className="text-sm text-white font-medium">{s.device}</div>
              <div className="text-xs text-gray-500">{s.location} · {s.time}</div>
            </div>
            {s.current ? <span className="text-xs text-green-400 font-medium">Current session</span> :
              <button className="text-xs text-red-400 hover:text-red-300 transition-colors">Revoke</button>}
          </div>
        ))}
      </div>
    </div>
  )
}
