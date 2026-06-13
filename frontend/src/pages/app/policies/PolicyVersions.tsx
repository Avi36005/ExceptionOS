import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Clock, User, RotateCcw } from 'lucide-react'

const versions = [
  { version: '2.3', date: '2024-10-15', author: 'Sarah Chen', changes: 'Added emergency exception provision with CISO sign-off requirement. Clarified vendor risk assessment scope.', current: true },
  { version: '2.2', date: '2024-07-01', author: 'Marcus Williams', changes: 'Updated budget threshold from $500 to $1,000. Added remote work software clause.', current: false },
  { version: '2.1', date: '2024-03-15', author: 'Jane Doe', changes: 'Extended review period from 21 to 30 days following security incident in Q1.', current: false },
  { version: '2.0', date: '2023-12-01', author: 'Tom Chen', changes: 'Major rewrite. Combined IT Security and Procurement policies. Added SaaS-specific requirements.', current: false },
  { version: '1.0', date: '2023-01-10', author: 'Sarah Chen', changes: 'Initial policy creation.', current: false },
]

export default function PolicyVersions() {
  const { policyId } = useParams()
  const navigate = useNavigate()

  return (
    <div className="fade-in max-w-2xl">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate(`/app/policies/${policyId}`)} className="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div>
          <h1 className="text-xl font-bold text-white">Version History</h1>
          <p className="text-sm text-gray-400">{policyId} · {versions.length} versions</p>
        </div>
      </div>

      <div className="relative">
        <div className="absolute left-4 top-0 bottom-0 w-px bg-white/10" />
        <div className="space-y-4">
          {versions.map(v => (
            <div key={v.version} className="relative flex gap-4">
              <div className={`relative z-10 w-8 h-8 rounded-full flex items-center justify-center shrink-0 border-2 ${v.current ? 'bg-primary border-primary' : 'bg-dark border-white/20'}`}>
                <span className="text-xs font-bold text-white">{v.version}</span>
              </div>
              <div className="flex-1 bg-dark2 rounded-xl border border-white/10 p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-white">v{v.version}</span>
                    {v.current && <span className="px-2 py-0.5 rounded-md text-xs bg-primary/20 text-primary font-medium">Current</span>}
                  </div>
                  {!v.current && (
                    <button className="flex items-center gap-1 text-xs text-gray-400 hover:text-white transition-colors">
                      <RotateCcw className="w-3 h-3" /> Restore
                    </button>
                  )}
                </div>
                <p className="text-sm text-gray-300 mb-3">{v.changes}</p>
                <div className="flex items-center gap-3 text-xs text-gray-500">
                  <span className="flex items-center gap-1"><User className="w-3 h-3" />{v.author}</span>
                  <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{v.date}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
