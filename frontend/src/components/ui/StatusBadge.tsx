type Status = 'draft' | 'submitted' | 'under_review' | 'approved' | 'rejected' | 'escalated' | 'pending' | 'active' | 'closed'
interface Props { status: Status }
export default function StatusBadge({ status }: Props) {
  const map: Record<Status, { label: string; class: string }> = {
    draft: { label: 'Draft', class: 'bg-gray-500/20 text-gray-400' },
    submitted: { label: 'Submitted', class: 'bg-blue-500/20 text-blue-400' },
    under_review: { label: 'Under Review', class: 'bg-yellow-500/20 text-yellow-400' },
    approved: { label: 'Approved', class: 'bg-green-500/20 text-green-400' },
    rejected: { label: 'Rejected', class: 'bg-red-500/20 text-red-400' },
    escalated: { label: 'Escalated', class: 'bg-orange-500/20 text-orange-400' },
    pending: { label: 'Pending', class: 'bg-yellow-500/20 text-yellow-400' },
    active: { label: 'Active', class: 'bg-green-500/20 text-green-400' },
    closed: { label: 'Closed', class: 'bg-gray-500/20 text-gray-400' },
  }
  const s = map[status] ?? { label: status, class: 'bg-gray-500/20 text-gray-400' }
  return <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium ${s.class}`}>{s.label}</span>
}
