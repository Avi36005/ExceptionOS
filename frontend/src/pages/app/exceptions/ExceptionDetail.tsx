import { Outlet, useNavigate, useParams, NavLink } from 'react-router-dom'
import { ArrowLeft, FileText, Shield, Search, MessageSquare, Brain, Gavel, BarChart2, ClipboardList, Archive, Clock, CheckCircle, AlertTriangle } from 'lucide-react'
import StatusBadge from '../../../components/ui/StatusBadge'
import { getCase } from '../../../lib/demoData'

const tabs = [
  { id: 'intake', label: 'Intake', icon: FileText },
  { id: 'evidence', label: 'Evidence', icon: Archive },
  { id: 'policy', label: 'Policy', icon: Shield },
  { id: 'precedents', label: 'Precedents', icon: Search },
  { id: 'debate', label: 'AI Debate', icon: MessageSquare },
  { id: 'recommendation', label: 'Recommendation', icon: Brain },
  { id: 'decision', label: 'Decision', icon: Gavel },
  { id: 'outcome', label: 'Outcome', icon: BarChart2 },
  { id: 'audit', label: 'Audit', icon: ClipboardList },
  { id: 'memory', label: 'Memory', icon: Archive },
]

const fallback = {
  title: 'Emergency software license for design team',
  status: 'under_review' as const, category: 'IT & Security', priority: 'high' as const,
  submitter: 'Alex Turner', created: '2024-12-18', deadline: '2024-12-20', amount: '$4,500', customer: 'Internal',
}

export default function ExceptionDetail() {
  const { caseId } = useParams()
  const navigate = useNavigate()
  const c = getCase(caseId)
  const mockException = c
    ? { ...c, submittedAt: c.created, department: c.customer }
    : { ...fallback, submittedAt: fallback.created, department: fallback.customer }

  return (
    <div className="fade-in">
      {/* Header */}
      <div className="flex items-start gap-3 mb-6">
        <button onClick={() => navigate('/app/my-requests')} className="p-2 rounded-lg hover:bg-gray-50 text-gray-500 hover:text-gray-900 transition-colors mt-1">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap mb-1">
            <span className="text-xs font-mono text-primary">{caseId}</span>
            <StatusBadge status={mockException.status} />
            <span className="px-2 py-0.5 rounded-md text-xs bg-red-50 text-red-700 ring-1 ring-red-600/20 font-medium">{mockException.priority} priority</span>
          </div>
          <h1 className="text-xl font-bold text-gray-900 mb-1">{mockException.title}</h1>
          <div className="flex items-center gap-4 text-xs text-gray-500 flex-wrap">
            <span className="flex items-center gap-1"><FileText className="w-3 h-3" />{mockException.category}</span>
            <span className="flex items-center gap-1"><Clock className="w-3 h-3" />Submitted {mockException.submittedAt}</span>
            <span className="flex items-center gap-1"><AlertTriangle className="w-3 h-3 text-orange-600" />Deadline: {mockException.deadline}</span>
            <span className="flex items-center gap-1"><CheckCircle className="w-3 h-3" />{mockException.submitter} · {mockException.department}</span>
            {mockException.amount && <span className="text-primary font-medium">{mockException.amount}</span>}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-0 border-b border-gray-200 mb-6 overflow-x-auto">
        {tabs.map(tab => (
          <NavLink
            key={tab.id}
            to={`/app/exceptions/${caseId}/${tab.id}`}
            className={({ isActive }) =>
              `flex items-center gap-1.5 px-3 py-3 text-xs font-medium whitespace-nowrap border-b-2 transition-all ${
                isActive ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-900'
              }`
            }
          >
            <tab.icon className="w-3.5 h-3.5" />
            {tab.label}
          </NavLink>
        ))}
      </div>

      {/* Tab content */}
      <Outlet />
    </div>
  )
}
