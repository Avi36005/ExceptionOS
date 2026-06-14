import { Brain, Tag, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const tags = ['IT Software', 'Emergency Procurement', 'Time-Sensitive', 'Figma', 'Design Team', 'SaaS License', 'Q4 2024', 'Conditional Approval']

const memoryInsights = [
  { label: 'Decision Pattern', value: 'This is the 3rd approved IT emergency exception in Q4. Pattern flagged for policy review.' },
  { label: 'Approval Conditions', value: '100% of similar IT emergency exceptions in the past 12 months were approved with time-limited conditions.' },
  { label: 'Avg Time to Decision', value: '6h 40m — 23% faster than organization average for IT exceptions (8h 36m).' },
  { label: 'Approver Consistency', value: 'Sarah Chen\'s decision is 96% consistent with her historical decisions on similar IT exceptions.' },
]

export default function ExceptionMemory() {
  const navigate = useNavigate()

  return (
    <div className="fade-in space-y-6">
      <div className="flex items-center gap-3 p-4 bg-primary/5 border border-primary/20 rounded-xl">
        <Brain className="w-5 h-5 text-primary shrink-0" />
        <div>
          <div className="text-sm font-semibold text-gray-900">Memory Committed</div>
          <div className="text-xs text-gray-500 mt-0.5">This exception has been added to the organizational memory. It will inform future similar decisions.</div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Tag className="w-4 h-4 text-gray-500" />
          <h3 className="text-sm font-semibold text-gray-900">Memory Tags</h3>
        </div>
        <div className="flex flex-wrap gap-2">
          {tags.map(tag => (
            <span key={tag} className="px-2.5 py-1 rounded-lg bg-primary/10 text-primary text-xs font-medium border border-primary/20">
              {tag}
            </span>
          ))}
        </div>
        <p className="text-xs text-gray-500 mt-3">AI automatically extracted these tags from the exception content, policy matches, and decision rationale.</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Memory Insights Generated</h3>
        <div className="space-y-4">
          {memoryInsights.map(insight => (
            <div key={insight.label} className="border-l-2 border-primary/30 pl-4">
              <div className="text-xs font-semibold text-primary mb-1">{insight.label}</div>
              <p className="text-sm text-gray-600">{insight.value}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Memory Availability</h3>
        <p className="text-sm text-gray-600 mb-4">
          This exception is now searchable in your precedent library and will be surfaced when similar requests are submitted.
          All personal information has been handled per your organization's data retention policy.
        </p>
        <button onClick={() => navigate('/app/precedents')} className="flex items-center gap-2 text-sm text-primary hover:text-primary-dark font-medium transition-colors">
          Browse precedent library <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
