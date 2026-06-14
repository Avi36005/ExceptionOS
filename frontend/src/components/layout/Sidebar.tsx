import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Inbox, FileText, CheckSquare, Plus,
  BookOpen, Search, BarChart3, GraduationCap, Mic,
  Plug, Settings, Users, Shield, Building2, AlertCircle,
  Clock, DollarSign, Tag, Activity, ChevronDown, ChevronRight,
  Zap, Brain
} from 'lucide-react'
import { useState } from 'react'
import { useOrgStore } from '../../store/orgStore'
import { useAuthStore } from '../../store/authStore'

interface NavGroup {
  label: string
  items: NavItem[]
}

interface NavItem {
  icon: React.ElementType
  label: string
  to: string
  adminOnly?: boolean
}

const navGroups: NavGroup[] = [
  {
    label: 'Overview',
    items: [
      { icon: LayoutDashboard, label: 'Dashboard', to: '/app' },
      { icon: Inbox, label: 'Inbox', to: '/app/inbox' },
      { icon: FileText, label: 'My Requests', to: '/app/my-requests' },
      { icon: CheckSquare, label: 'My Approvals', to: '/app/my-approvals' },
    ],
  },
  {
    label: 'Exceptions',
    items: [
      { icon: BookOpen, label: 'Policy Library', to: '/app/policies' },
      { icon: Search, label: 'Precedents', to: '/app/precedents' },
      { icon: Brain, label: 'Ask Memory', to: '/app/precedents/ask' },
    ],
  },
  {
    label: 'Intelligence',
    items: [
      { icon: BarChart3, label: 'Insights', to: '/app/insights' },
      { icon: GraduationCap, label: 'Training', to: '/app/training' },
      { icon: Mic, label: 'Voice Assistant', to: '/app/voice' },
      { icon: Plug, label: 'Integrations', to: '/app/integrations' },
    ],
  },
  {
    label: 'Administration',
    items: [
      { icon: Building2, label: 'Organizations', to: '/app/admin/organizations', adminOnly: true },
      { icon: Users, label: 'Users', to: '/app/admin/users', adminOnly: true },
      { icon: Shield, label: 'Roles', to: '/app/admin/roles', adminOnly: true },
      { icon: Tag, label: 'Departments', to: '/app/admin/departments', adminOnly: true },
      { icon: AlertCircle, label: 'Escalation Rules', to: '/app/admin/escalation', adminOnly: true },
      { icon: Clock, label: 'SLA Config', to: '/app/admin/sla', adminOnly: true },
      { icon: DollarSign, label: 'Budgets', to: '/app/admin/budgets', adminOnly: true },
      { icon: Tag, label: 'Categories', to: '/app/admin/categories', adminOnly: true },
      { icon: Activity, label: 'System Health', to: '/app/admin/system', adminOnly: true },
    ],
  },
]

export default function Sidebar({ collapsed }: { collapsed: boolean }) {
  const { isAdmin } = useOrgStore()
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const [collapsedGroups, setCollapsedGroups] = useState<Record<string, boolean>>({})

  const toggleGroup = (label: string) => {
    setCollapsedGroups(prev => ({ ...prev, [label]: !prev[label] }))
  }

  const linkClass = (isActive: boolean) =>
    `group relative flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
      isActive
        ? 'text-white bg-primary/25 shadow-[inset_0_0_0_1px_rgba(91,91,240,.35)]'
        : 'text-slate-400 hover:text-white hover:bg-white/[0.06]'
    } ${collapsed ? 'justify-center' : ''}`

  return (
    <aside
      className={`flex flex-col h-full bg-gradient-to-b from-sidebar to-sidebar-2 border-r border-white/[0.06] shadow-sidebar transition-all duration-200 ${
        collapsed ? 'w-16' : 'w-60'
      }`}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-16 border-b border-white/[0.06] shrink-0">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-[#7C5CFF] flex items-center justify-center shrink-0 shadow-[0_4px_14px_rgba(91,91,240,.45)]">
          <Zap className="w-4 h-4 text-white" />
        </div>
        {!collapsed && (
          <div>
            <div className="text-sm font-bold text-white leading-none">ExceptionOS</div>
            <div className="text-xs text-slate-500 leading-none mt-0.5">Decision Intelligence</div>
          </div>
        )}
      </div>

      {/* New Exception CTA */}
      {!collapsed && (
        <div className="px-3 pt-3">
          <button
            onClick={() => navigate('/app/exceptions/new')}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-sm font-medium transition-colors shadow-[0_6px_18px_rgba(91,91,240,.35)]"
          >
            <Plus className="w-4 h-4" />
            New Exception
          </button>
        </div>
      )}
      {collapsed && (
        <div className="px-2 pt-3">
          <button
            onClick={() => navigate('/app/exceptions/new')}
            className="w-full flex items-center justify-center p-2 rounded-lg bg-primary hover:bg-primary-dark text-white transition-colors"
            title="New Exception"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Navigation */}
      <nav className="sidebar-scroll flex-1 overflow-y-auto py-3 px-2 space-y-1">
        {navGroups.map(group => {
          const filteredItems = group.items.filter(item => !item.adminOnly || isAdmin())
          if (filteredItems.length === 0) return null
          const isGroupCollapsed = collapsedGroups[group.label]

          return (
            <div key={group.label} className="mb-1">
              {!collapsed && (
                <button
                  onClick={() => toggleGroup(group.label)}
                  className="w-full flex items-center justify-between px-3 py-1 mb-1"
                >
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">{group.label}</span>
                  {isGroupCollapsed ? <ChevronRight className="w-3 h-3 text-slate-600" /> : <ChevronDown className="w-3 h-3 text-slate-600" />}
                </button>
              )}
              {!isGroupCollapsed && (
                <div className="space-y-0.5">
                  {filteredItems.map(item => (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      end={item.to === '/app'}
                      className={({ isActive }) => linkClass(isActive)}
                      title={collapsed ? item.label : undefined}
                    >
                      {({ isActive }) => (
                        <>
                          {isActive && !collapsed && (
                            <span className="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-1 rounded-r-full bg-primary" />
                          )}
                          <item.icon className="w-4 h-4 shrink-0" />
                          {!collapsed && <span>{item.label}</span>}
                        </>
                      )}
                    </NavLink>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </nav>

      {/* Bottom: Settings + User */}
      <div className="border-t border-white/[0.06] p-2 space-y-0.5">
        <NavLink
          to="/app/settings/profile"
          className={({ isActive }) => linkClass(isActive)}
          title={collapsed ? 'Settings' : undefined}
        >
          <Settings className="w-4 h-4 shrink-0" />
          {!collapsed && <span>Settings</span>}
        </NavLink>
        {!collapsed && (
          <div className="flex items-center gap-3 px-3 py-2 mt-1">
            <div className="w-7 h-7 rounded-full bg-primary/30 flex items-center justify-center text-xs font-bold text-white shrink-0">
              {user?.email?.[0]?.toUpperCase() ?? 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium text-white truncate">{user?.user_metadata?.full_name || 'User'}</div>
              <div className="text-xs text-slate-500 truncate">{user?.email}</div>
            </div>
          </div>
        )}
      </div>
    </aside>
  )
}
