import { Bell, Search, ChevronDown, LogOut, User, Menu, Settings, Building2 } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { useOrgStore } from '../../store/orgStore'

interface Props {
  onToggleSidebar: () => void
}

export default function TopBar({ onToggleSidebar }: Props) {
  const { user, signOut } = useAuthStore()
  const { currentOrg } = useOrgStore()
  const navigate = useNavigate()
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [notifOpen, setNotifOpen] = useState(false)
  const userMenuRef = useRef<HTMLDivElement>(null)
  const notifRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) setUserMenuOpen(false)
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) setNotifOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const handleSignOut = async () => {
    await signOut()
    navigate('/login')
  }

  const mockNotifications = [
    { id: 1, text: 'EXC-1042 approved by Sarah Chen', time: '2m ago', unread: true },
    { id: 2, text: 'New exception requires your review', time: '15m ago', unread: true },
    { id: 3, text: 'Policy "Vendor NDA" was updated', time: '1h ago', unread: false },
  ]

  return (
    <header className="h-16 border-b border-gray-200 bg-white flex items-center px-4 gap-4 shrink-0">
      {/* Sidebar toggle */}
      <button
        onClick={onToggleSidebar}
        className="p-2 rounded-lg text-gray-500 hover:text-gray-900 hover:bg-gray-100 transition-colors"
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* Org name */}
      {currentOrg && (
        <button
          onClick={() => navigate('/select-organization')}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors border border-gray-200"
        >
          <Building2 className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium text-gray-900">{currentOrg.name}</span>
          <ChevronDown className="w-3 h-3 text-gray-400" />
        </button>
      )}

      {/* Search */}
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search exceptions, policies, precedents..."
            className="w-full bg-gray-50 border border-gray-200 rounded-lg pl-10 pr-4 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:bg-white focus:border-primary/50 focus:ring-2 focus:ring-primary/15 transition-all"
          />
          <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400 bg-white px-1.5 py-0.5 rounded border border-gray-200">⌘K</kbd>
        </div>
      </div>

      <div className="flex items-center gap-2 ml-auto">
        {/* Notifications */}
        <div className="relative" ref={notifRef}>
          <button
            onClick={() => setNotifOpen(!notifOpen)}
            className="relative p-2 rounded-lg text-gray-500 hover:text-gray-900 hover:bg-gray-100 transition-colors"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-primary rounded-full pulse-dot" />
          </button>
          {notifOpen && (
            <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-xl border border-gray-200 shadow-card-hover z-50 fade-in">
              <div className="p-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-gray-900">Notifications</h3>
                  <span className="text-xs text-primary cursor-pointer">Mark all read</span>
                </div>
              </div>
              <div className="divide-y divide-gray-100">
                {mockNotifications.map(n => (
                  <div key={n.id} className={`flex gap-3 p-4 hover:bg-gray-50 cursor-pointer ${n.unread ? '' : 'opacity-60'}`}>
                    {n.unread && <div className="w-2 h-2 bg-primary rounded-full mt-1.5 shrink-0" />}
                    {!n.unread && <div className="w-2 h-2 mt-1.5 shrink-0" />}
                    <div>
                      <p className="text-sm text-gray-900">{n.text}</p>
                      <p className="text-xs text-gray-400 mt-0.5">{n.time}</p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="p-3 border-t border-gray-200">
                <button className="w-full text-xs text-gray-500 hover:text-gray-900 text-center transition-colors">View all notifications</button>
              </div>
            </div>
          )}
        </div>

        {/* User menu */}
        <div className="relative" ref={userMenuRef}>
          <button
            onClick={() => setUserMenuOpen(!userMenuOpen)}
            className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div className="w-7 h-7 rounded-full bg-primary/15 flex items-center justify-center text-xs font-bold text-primary">
              {user?.email?.[0]?.toUpperCase() ?? 'U'}
            </div>
            <span className="text-sm text-gray-900 hidden sm:block">{user?.user_metadata?.full_name?.split(' ')[0] || 'User'}</span>
            <ChevronDown className="w-3 h-3 text-gray-400" />
          </button>
          {userMenuOpen && (
            <div className="absolute right-0 top-full mt-2 w-52 bg-white rounded-xl border border-gray-200 shadow-card-hover z-50 fade-in overflow-hidden">
              <div className="p-3 border-b border-gray-200">
                <div className="text-sm font-medium text-gray-900">{user?.user_metadata?.full_name || 'User'}</div>
                <div className="text-xs text-gray-400">{user?.email}</div>
              </div>
              <div className="p-1">
                <button
                  onClick={() => { navigate('/app/settings/profile'); setUserMenuOpen(false) }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
                >
                  <User className="w-4 h-4" />
                  Profile
                </button>
                <button
                  onClick={() => { navigate('/app/settings/org'); setUserMenuOpen(false) }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
                >
                  <Settings className="w-4 h-4" />
                  Organization
                </button>
              </div>
              <div className="p-1 border-t border-gray-200">
                <button
                  onClick={handleSignOut}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  Sign out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
