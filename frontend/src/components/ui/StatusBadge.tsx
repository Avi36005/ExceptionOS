type Status = 'draft' | 'submitted' | 'under_review' | 'approved' | 'rejected' | 'escalated' | 'pending' | 'active' | 'closed'
interface Props { status: Status }
export default function StatusBadge({ status }: Props) {
  const map: Record<Status, { label: string; class: string }> = {
    draft: { label: 'Draft', class: 'bg-gray-100 text-gray-600 ring-1 ring-gray-200' },
    submitted: { label: 'Submitted', class: 'bg-blue-50 text-blue-700 ring-1 ring-blue-200' },
    under_review: { label: 'Under Review', class: 'bg-amber-50 text-amber-700 ring-1 ring-amber-200' },
    approved: { label: 'Approved', class: 'bg-green-50 text-green-700 ring-1 ring-green-200' },
    rejected: { label: 'Rejected', class: 'bg-red-50 text-red-700 ring-1 ring-red-200' },
    escalated: { label: 'Escalated', class: 'bg-orange-50 text-orange-700 ring-1 ring-orange-200' },
    pending: { label: 'Pending', class: 'bg-amber-50 text-amber-700 ring-1 ring-amber-200' },
    active: { label: 'Active', class: 'bg-green-50 text-green-700 ring-1 ring-green-200' },
    closed: { label: 'Closed', class: 'bg-gray-100 text-gray-600 ring-1 ring-gray-200' },
  }
  const s = map[status] ?? { label: status, class: 'bg-gray-100 text-gray-600 ring-1 ring-gray-200' }
  return <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium ${s.class}`}>{s.label}</span>
}
