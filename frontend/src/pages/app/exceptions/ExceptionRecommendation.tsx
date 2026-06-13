import { Brain, CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'

const conditions = [
  'CISO security sign-off required within 24 hours of approval',
  'License limited to 90 days (emergency provision) — full procurement to be completed in parallel',
  'Q4 IT procurement retrospective to be completed by Jan 15 to address recurring emergency pattern',
  'Usage restricted to design team only (max 8 seats)',
]

const riskFactors = [
  { label: 'Business Impact Risk', level: 'high', desc: '$120K revenue exposure if rejected' },
  { label: 'Policy Compliance Risk', level: 'medium', desc: '1 violated policy, 1 partial' },
  { label: 'Precedent Risk', level: 'medium', desc: '3rd IT emergency exception this quarter' },
  { label: 'Security Risk', level: 'low', desc: 'Known vendor with existing security approval' },
]

const levelColors: Record<string, string> = {
  high: 'bg-red-500/20 text-red-400',
  medium: 'bg-yellow-500/20 text-yellow-400',
  low: 'bg-green-500/20 text-green-400',
}

export default function ExceptionRecommendation() {
  const navigate = useNavigate()
  const { caseId } = useParams()

  return (
    <div className="fade-in space-y-6">
      {/* Main recommendation */}
      <div className="bg-green-500/5 border border-green-500/30 rounded-xl p-6">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-green-500/10 flex items-center justify-center shrink-0">
            <Brain className="w-6 h-6 text-green-400" />
          </div>
          <div>
            <div className="text-xs font-semibold text-green-400 mb-1 uppercase tracking-wide">AI Recommendation</div>
            <div className="text-xl font-bold text-white mb-2">Approve with Conditions</div>
            <p className="text-sm text-gray-300 leading-relaxed">
              Based on analysis of 4 precedents, 3 relevant policies, and the business justification provided, ExceptionOS recommends conditional approval.
              The business impact is significant and quantifiable, and the organizational risk can be mitigated through the conditions listed below.
            </p>
            <div className="flex items-center gap-2 mt-3">
              <span className="text-sm font-semibold text-white">Confidence:</span>
              <div className="flex items-center gap-1">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className={`w-2 h-5 rounded-sm ${i < 4 ? 'bg-green-400' : 'bg-white/20'}`} />
                ))}
              </div>
              <span className="text-sm text-green-400 font-medium">82%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Conditions */}
      <div className="bg-dark2 rounded-xl border border-white/10 p-6">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-4 h-4 text-yellow-400" />
          <h3 className="text-sm font-semibold text-white">Required Conditions for Approval</h3>
        </div>
        <div className="space-y-3">
          {conditions.map((c, i) => (
            <div key={i} className="flex items-start gap-3">
              <CheckCircle className="w-4 h-4 text-yellow-400 shrink-0 mt-0.5" />
              <p className="text-sm text-gray-300">{c}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Risk assessment */}
      <div className="bg-dark2 rounded-xl border border-white/10 p-6">
        <h3 className="text-sm font-semibold text-white mb-4">Risk Assessment</h3>
        <div className="space-y-3">
          {riskFactors.map(r => (
            <div key={r.label} className="flex items-center gap-3">
              <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize shrink-0 w-16 text-center ${levelColors[r.level]}`}>{r.level}</span>
              <div className="flex-1">
                <div className="text-xs font-medium text-white">{r.label}</div>
                <div className="text-xs text-gray-500">{r.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <button onClick={() => navigate(`/app/exceptions/${caseId}/decision`)}
        className="flex items-center gap-2 px-6 py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold transition-colors">
        Proceed to Decision <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  )
}
