import { Activity, CheckCircle, AlertTriangle, XCircle } from 'lucide-react'

const services = [
  { name: 'API Gateway', status: 'healthy', uptime: '99.98%', latency: '42ms', lastCheck: '1m ago' },
  { name: 'AI Decision Engine', status: 'healthy', uptime: '99.95%', latency: '1.2s', lastCheck: '1m ago' },
  { name: 'Database (Supabase)', status: 'healthy', uptime: '99.99%', latency: '12ms', lastCheck: '30s ago' },
  { name: 'Memory Index', status: 'warning', uptime: '99.82%', latency: '380ms', lastCheck: '2m ago' },
  { name: 'Email Notifications', status: 'healthy', uptime: '99.90%', latency: '250ms', lastCheck: '1m ago' },
  { name: 'Webhook Queue', status: 'healthy', uptime: '99.97%', latency: '85ms', lastCheck: '1m ago' },
]

const statusConfig = {
  healthy: { icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-500/10', label: 'Healthy' },
  warning: { icon: AlertTriangle, color: 'text-yellow-400', bg: 'bg-yellow-500/10', label: 'Warning' },
  error: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/10', label: 'Error' },
}

export default function SystemHealth() {
  const healthy = services.filter(s => s.status === 'healthy').length

  return (
    <div className="fade-in">
      <div className="flex items-center gap-3 mb-6">
        <Activity className="w-6 h-6 text-primary" />
        <div>
          <h1 className="text-2xl font-bold text-white">System Health</h1>
          <p className="text-sm text-gray-400 mt-1">{healthy}/{services.length} services operational</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { label: 'Overall Uptime', value: '99.95%', color: 'text-green-400' },
          { label: 'Active Users', value: '47', color: 'text-white' },
          { label: 'Exceptions Today', value: '12', color: 'text-white' },
        ].map(s => (
          <div key={s.label} className="bg-dark2 rounded-xl border border-white/10 p-4">
            <div className="text-xs text-gray-500 mb-1">{s.label}</div>
            <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
          </div>
        ))}
      </div>

      <div className="bg-dark2 rounded-xl border border-white/10 divide-y divide-white/5">
        {services.map(s => {
          const cfg = statusConfig[s.status as keyof typeof statusConfig]
          const Icon = cfg.icon
          return (
            <div key={s.name} className="flex items-center gap-4 p-4">
              <div className={`w-8 h-8 rounded-lg ${cfg.bg} flex items-center justify-center shrink-0`}>
                <Icon className={`w-4 h-4 ${cfg.color}`} />
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium text-white">{s.name}</div>
                <div className="text-xs text-gray-500">Last checked {s.lastCheck}</div>
              </div>
              <div className="text-right text-xs">
                <div className="text-gray-300">{s.uptime} uptime</div>
                <div className="text-gray-500">{s.latency} avg</div>
              </div>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${cfg.bg} ${cfg.color}`}>{cfg.label}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
