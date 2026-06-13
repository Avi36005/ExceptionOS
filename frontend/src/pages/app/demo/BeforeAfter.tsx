import { useNavigate } from 'react-router-dom'
import { ArrowLeft, X, CheckCircle, ArrowRight } from 'lucide-react'

const comparisons = [
  { aspect: 'Decision time', before: '3-5 days average', after: 'Under 8 hours average' },
  { aspect: 'Policy consistency', before: 'Varies by approver', after: '96% consistency score' },
  { aspect: 'Audit trail', before: 'Email threads, PDFs', after: 'Complete digital record' },
  { aspect: 'Precedent lookup', before: 'Manual research', after: 'Instant AI search' },
  { aspect: 'Pattern detection', before: 'Quarterly reports', after: 'Real-time alerts' },
  { aspect: 'Institutional memory', before: 'Leaves with employees', after: 'Preserved forever' },
]

export default function BeforeAfter() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-dark flex flex-col items-center justify-center p-6">
      <button onClick={() => navigate('/demo')} className="absolute top-6 left-6 flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back
      </button>
      <div className="max-w-3xl w-full">
        <h1 className="text-3xl font-bold text-white text-center mb-2">Before vs. After ExceptionOS</h1>
        <p className="text-gray-400 text-center mb-8">The difference intelligent exception management makes.</p>

        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center text-sm font-semibold text-gray-400 pt-4">Aspect</div>
          <div className="bg-red-500/5 border border-red-500/20 rounded-xl p-3 text-center">
            <span className="text-sm font-semibold text-red-400">Without ExceptionOS</span>
          </div>
          <div className="bg-green-500/5 border border-green-500/20 rounded-xl p-3 text-center">
            <span className="text-sm font-semibold text-green-400">With ExceptionOS</span>
          </div>
        </div>

        <div className="space-y-2">
          {comparisons.map(c => (
            <div key={c.aspect} className="grid grid-cols-3 gap-4 items-center">
              <div className="text-sm text-gray-300 font-medium py-3">{c.aspect}</div>
              <div className="bg-red-500/5 border border-red-500/10 rounded-xl p-3 flex items-center gap-2">
                <X className="w-4 h-4 text-red-400 shrink-0" />
                <span className="text-xs text-red-300">{c.before}</span>
              </div>
              <div className="bg-green-500/5 border border-green-500/10 rounded-xl p-3 flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-400 shrink-0" />
                <span className="text-xs text-green-300">{c.after}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center mt-8">
          <button onClick={() => navigate('/signup')} className="flex items-center gap-2 px-8 py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold transition-colors mx-auto">
            Start your free trial <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
