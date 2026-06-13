import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, CheckCircle, Tag, User, Calendar, BookOpen } from 'lucide-react'

export default function PrecedentDetail() {
  const { precedentId } = useParams()
  const navigate = useNavigate()

  return (
    <div className="fade-in max-w-3xl">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate('/app/precedents')} className="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono text-gray-500">{precedentId}</span>
            <span className="px-2 py-0.5 rounded-md text-xs bg-green-500/20 text-green-400 font-medium flex items-center gap-1"><CheckCircle className="w-3 h-3" />Approved</span>
          </div>
          <h1 className="text-xl font-bold text-white">Emergency Figma licenses for product launch</h1>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-dark2 rounded-xl border border-white/10 p-5">
            <h3 className="text-sm font-semibold text-white mb-3">Context</h3>
            <p className="text-sm text-gray-300 leading-relaxed">Design team required Figma Enterprise access for a customer-facing product prototype needed for a board presentation. Standard procurement would have taken 30 days; the deadline was 5 days away.</p>
          </div>
          <div className="bg-dark2 rounded-xl border border-white/10 p-5">
            <h3 className="text-sm font-semibold text-white mb-3">Decision Rationale</h3>
            <p className="text-sm text-gray-300 leading-relaxed">Approved under emergency provision (POL-IT-004 §4.2). Business impact was quantified at $200K in potential revenue. Vendor was already vetted. CISO expedited security review completed in 8 hours. License capped at 60 days with parallel procurement initiated.</p>
          </div>
          <div className="bg-dark2 rounded-xl border border-white/10 p-5">
            <h3 className="text-sm font-semibold text-white mb-3">Outcome</h3>
            <p className="text-sm text-gray-300 leading-relaxed">Board presentation successful. Customer contract signed ($1.2M ARR). Standard procurement completed within the 60-day window. No security incidents. Pattern contributed to emergency exception provision being added to IT policy in v2.3.</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-dark2 rounded-xl border border-white/10 p-4">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Details</h3>
            <div className="space-y-3 text-sm">
              {[
                { icon: Calendar, label: 'Date', value: 'Sep 12, 2024' },
                { icon: User, label: 'Approver', value: 'Sarah Chen' },
                { icon: BookOpen, label: 'Category', value: 'IT & Security' },
                { icon: Tag, label: 'Amount', value: '$3,200/yr' },
              ].map(d => (
                <div key={d.label} className="flex items-center gap-2">
                  <d.icon className="w-4 h-4 text-gray-600 shrink-0" />
                  <span className="text-gray-500 w-20 shrink-0">{d.label}</span>
                  <span className="text-gray-300">{d.value}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-dark2 rounded-xl border border-white/10 p-4">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Tags</h3>
            <div className="flex flex-wrap gap-1.5">
              {['Emergency', 'SaaS', 'Design', 'Figma', 'Product Launch'].map(t => (
                <span key={t} className="px-2 py-0.5 rounded-md text-xs bg-primary/10 text-primary border border-primary/20">{t}</span>
              ))}
            </div>
          </div>
          <div className="bg-dark2 rounded-xl border border-white/10 p-4">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Similar Precedents</h3>
            <div className="space-y-2">
              {['PREC-0198', 'PREC-0142'].map(id => (
                <button key={id} onClick={() => navigate(`/app/precedents/${id}`)} className="w-full text-left text-sm text-primary hover:text-primary-dark transition-colors">{id}</button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
