import { Search, CheckCircle, XCircle, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const precedents = [
  { id: 'PREC-0234', title: 'Emergency Figma licenses for product launch', date: '2024-09-12', decision: 'approved', similarity: 94, rationale: 'Similar time-sensitive requirement with documented business impact. Approved with 60-day limit and security review.' },
  { id: 'PREC-0198', title: 'Adobe Creative Suite emergency procurement', date: '2024-06-03', decision: 'approved', similarity: 87, rationale: 'Approved under emergency provision. Required CISO sign-off and expedited security review completed within 24hrs.' },
  { id: 'PREC-0156', title: 'Slack enterprise upgrade outside procurement', date: '2024-02-14', decision: 'rejected', similarity: 72, rationale: 'Rejected - insufficient business justification, standard procurement timeline was achievable with minor project adjustment.' },
  { id: 'PREC-0142', title: 'Zoom Webinar license emergency', date: '2023-11-28', decision: 'approved', similarity: 68, rationale: 'Approved with VP-level sign-off. Customer-facing event created genuine emergency circumstances.' },
]

export default function ExceptionPrecedents() {
  const navigate = useNavigate()
  return (
    <div className="fade-in space-y-4">
      <div className="flex items-center gap-3 p-4 bg-primary/5 border border-primary/20 rounded-xl">
        <Search className="w-5 h-5 text-primary shrink-0" />
        <div>
          <div className="text-sm font-semibold text-white">4 similar precedents found</div>
          <div className="text-xs text-gray-400 mt-0.5">AI found 3 approved and 1 rejected precedent. Approval rate for similar IT emergency exceptions: 82%.</div>
        </div>
      </div>

      {precedents.map(p => (
        <div key={p.id} className="bg-dark2 rounded-xl border border-white/10 p-5">
          <div className="flex items-start justify-between gap-4 mb-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-mono text-gray-500">{p.id}</span>
                <span className="text-xs text-gray-600">·</span>
                <span className="text-xs text-gray-500">{p.date}</span>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${p.similarity}% match flex items-center gap-1`}></span>
              </div>
              <h3 className="text-sm font-semibold text-white">{p.title}</h3>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium ${p.decision === 'approved' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                {p.decision === 'approved' ? <CheckCircle className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                {p.decision.charAt(0).toUpperCase() + p.decision.slice(1)}
              </div>
              <span className="text-xs text-primary font-semibold">{p.similarity}% match</span>
            </div>
          </div>
          <p className="text-xs text-gray-400 leading-relaxed mb-3 italic">"{p.rationale}"</p>
          <button onClick={() => navigate(`/app/precedents/${p.id}`)} className="flex items-center gap-1 text-xs text-primary hover:text-primary-dark font-medium transition-colors">
            View full precedent <ArrowRight className="w-3 h-3" />
          </button>
        </div>
      ))}
    </div>
  )
}
