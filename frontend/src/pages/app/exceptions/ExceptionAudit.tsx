import { Clock, User, FileText, MessageSquare, CheckCircle, Eye, Send } from 'lucide-react'

const auditEvents = [
  { id: 1, type: 'submitted', icon: Send, color: 'text-blue-400', actor: 'Alex Turner', action: 'submitted the exception request', time: 'Dec 18, 2024 9:02 AM', details: 'Initial submission with 4 supporting documents' },
  { id: 2, type: 'viewed', icon: Eye, color: 'text-gray-400', actor: 'Sarah Chen', action: 'viewed the exception', time: 'Dec 18, 2024 10:15 AM', details: null },
  { id: 3, type: 'ai_analysis', icon: FileText, color: 'text-primary', actor: 'Hindsight™ AI', action: 'completed policy and precedent analysis', time: 'Dec 18, 2024 10:15 AM', details: '3 relevant policies, 4 precedents found, confidence: 82%' },
  { id: 4, type: 'comment', icon: MessageSquare, color: 'text-yellow-400', actor: 'Sarah Chen', action: 'requested additional information', time: 'Dec 18, 2024 11:30 AM', details: '"Please provide vendor quote and project timeline documentation"' },
  { id: 5, type: 'uploaded', icon: FileText, color: 'text-green-400', actor: 'Alex Turner', action: 'uploaded 2 additional documents', time: 'Dec 18, 2024 1:45 PM', details: 'Vendor_Quote_Figma_Enterprise.pdf, Project_Timeline_Q1_Launch.xlsx' },
  { id: 6, type: 'viewed', icon: Eye, color: 'text-gray-400', actor: 'Marcus Williams', action: 'viewed the exception', time: 'Dec 18, 2024 2:10 PM', details: null },
  { id: 7, type: 'comment', icon: MessageSquare, color: 'text-blue-400', actor: 'Marcus Williams', action: 'added comment', time: 'Dec 18, 2024 2:22 PM', details: '"Concur with the AI recommendation. Business case is solid."' },
  { id: 8, type: 'decided', icon: CheckCircle, color: 'text-green-400', actor: 'Sarah Chen', action: 'approved with conditions', time: 'Dec 18, 2024 3:42 PM', details: '4 conditions attached. Decision rationale recorded.' },
  { id: 9, type: 'notified', icon: Send, color: 'text-primary', actor: 'ExceptionOS', action: 'sent notifications to all stakeholders', time: 'Dec 18, 2024 3:42 PM', details: 'Requester, CISO, procurement team notified' },
]

export default function ExceptionAudit() {
  return (
    <div className="fade-in space-y-4">
      <div className="flex items-center gap-3 p-4 bg-white/5 border border-white/10 rounded-xl">
        <Clock className="w-5 h-5 text-primary shrink-0" />
        <div>
          <div className="text-sm font-semibold text-white">Complete Audit Trail</div>
          <div className="text-xs text-gray-400 mt-0.5">Every action on this exception is permanently recorded and tamper-proof. Total time to decision: 6h 40m</div>
        </div>
      </div>

      <div className="bg-dark2 rounded-xl border border-white/10 p-6">
        <div className="relative">
          <div className="absolute left-4 top-0 bottom-0 w-px bg-white/10" />
          <div className="space-y-6">
            {auditEvents.map(event => (
              <div key={event.id} className="relative flex gap-4">
                <div className={`relative z-10 w-8 h-8 rounded-full bg-dark border-2 border-white/10 flex items-center justify-center shrink-0`}>
                  <event.icon className={`w-3.5 h-3.5 ${event.color}`} />
                </div>
                <div className="flex-1 min-w-0 pt-1">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="text-sm font-medium text-white">{event.actor}</span>
                      <span className="text-sm text-gray-400"> {event.action}</span>
                    </div>
                    <span className="text-xs text-gray-600 shrink-0">{event.time}</span>
                  </div>
                  {event.details && (
                    <p className="text-xs text-gray-500 mt-1 leading-relaxed">{event.details}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex gap-3">
        <button className="flex-1 py-2.5 rounded-lg bg-white/10 hover:bg-white/15 text-white font-medium text-sm border border-white/10 transition-colors">
          Export Audit Log (PDF)
        </button>
        <button className="flex-1 py-2.5 rounded-lg bg-white/10 hover:bg-white/15 text-white font-medium text-sm border border-white/10 transition-colors">
          Export to CSV
        </button>
      </div>
    </div>
  )
}
