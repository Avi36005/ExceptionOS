/**
 * Shared demo dataset — the 10 exception cases that are ALSO seeded into the
 * Hindsight bank (synthetic-bank-acme via scripts/synthetic/seed_demo_examples.py).
 * Wired into the dashboard list/detail pages so the UI and the Hindsight-backed
 * orb/Ask-Memory tell the same story in a demo video.
 */

export type CaseStatus =
  | 'submitted' | 'under_review' | 'approved' | 'rejected' | 'closed'

export interface DemoCase {
  id: string
  title: string
  customer: string
  category: string
  status: CaseStatus
  priority: 'high' | 'medium' | 'low'
  amount: string
  days: number
  submitter: string
  approver: string
  created: string
  deadline: string
  reason: string
  recommendation: string
  decision: string
  outcome: string
  precedents: string[]
}

export const DEMO_CASES: DemoCase[] = [
  {
    id: 'EX-108', title: 'Late refund after integration failure', customer: 'Acme Retail',
    category: 'Refund', status: 'approved', priority: 'high', amount: '₹1,20,000', days: 52,
    submitter: 'Alex Turner', approver: 'Marcus Williams (CFO)', created: '2026-06-02', deadline: '2026-06-05',
    reason: 'Integration failed (confirmed NovaFlow fault); only partial service delivered.',
    recommendation: 'Approve a 75% refund (₹90,000) + one free month.',
    decision: 'CFO overrode to a FULL ₹1,20,000 refund to protect a ₹20,00,000 expansion.',
    outcome: 'Acme stayed and signed the ₹20,00,000 expansion. Success score 90/100.',
    precedents: ['BrightLabs', 'DataPeak', 'SkyBridge'],
  },
  {
    id: 'EX-109', title: 'Refund request — integration failure (no expansion)', customer: 'PixelWorks',
    category: 'Refund', status: 'under_review', priority: 'high', amount: '₹1,20,000', days: 50,
    submitter: 'Dana Wells', approver: 'Marcus Williams (CFO)', created: '2026-06-12', deadline: '2026-06-16',
    reason: 'Integration failed (NovaFlow fault), partial service. No expansion opportunity.',
    recommendation: 'Approve 60–70% refund — do NOT copy Acme’s full refund (no expansion factor).',
    decision: 'Pending CFO decision.',
    outcome: 'Awaiting decision.',
    precedents: ['Acme Retail', 'DataPeak', 'BrightLabs'],
  },
  {
    id: 'EX-110', title: '25% enterprise discount above 15% cap', customer: 'SummitLedger',
    category: 'Discount', status: 'under_review', priority: 'medium', amount: '₹4,20,000/yr', days: 0,
    submitter: 'Ravi Menon', approver: 'Marcus Williams (CFO)', created: '2026-06-11', deadline: '2026-06-15',
    reason: 'Requests 25% discount (cap is 15%) citing a 3-year commitment.',
    recommendation: 'Approve 20%; CFO may approve 25% for multi-year lock-in.',
    decision: 'Pending CFO decision.',
    outcome: 'Awaiting decision.',
    precedents: ['Globex', 'DataPeak'],
  },
  {
    id: 'EX-101', title: 'Late refund — partial service', customer: 'BrightLabs',
    category: 'Refund', status: 'approved', priority: 'medium', amount: '₹60,000', days: 47,
    submitter: 'Nina Roy', approver: 'Sarah Chen', created: '2026-05-12', deadline: '2026-05-15',
    reason: 'NovaFlow-caused integration failure; partial service delivered.',
    recommendation: 'Approve 50% partial refund.',
    decision: 'Approved 50% refund.',
    outcome: 'BrightLabs accepted and remained a customer.',
    precedents: ['DataPeak'],
  },
  {
    id: 'EX-102', title: 'Late refund — partial service', customer: 'DataPeak',
    category: 'Refund', status: 'closed', priority: 'medium', amount: '₹72,000', days: 46,
    submitter: 'Omar Faruk', approver: 'Sarah Chen', created: '2026-05-08', deadline: '2026-05-11',
    reason: 'NovaFlow caused the problem; partial service delivered.',
    recommendation: 'Approve 60% partial refund.',
    decision: 'Approved 60% refund.',
    outcome: 'DataPeak renewed its annual contract.',
    precedents: ['BrightLabs'],
  },
  {
    id: 'EX-103', title: 'Late refund — customer-caused delay', customer: 'SkyBridge',
    category: 'Refund', status: 'rejected', priority: 'medium', amount: '₹95,000', days: 55,
    submitter: 'Liu Wei', approver: 'Sarah Chen', created: '2026-05-02', deadline: '2026-05-05',
    reason: 'Delay was caused by the customer’s own staffing, not NovaFlow.',
    recommendation: 'Reject — outside policy, internal fault not established.',
    decision: 'Rejected per policy.',
    outcome: 'SkyBridge cancelled its contract.',
    precedents: ['Acme Retail'],
  },
  {
    id: 'EX-104', title: 'Payment-terms extension (net-30 → net-90)', customer: 'Initech',
    category: 'Finance', status: 'rejected', priority: 'high', amount: '₹3,00,000', days: 0,
    submitter: 'Grace Park', approver: 'Marcus Williams (CFO)', created: '2026-05-20', deadline: '2026-05-23',
    reason: 'Requests net-90 terms; memory shows a prior payment default.',
    recommendation: 'Deny — prior default raises bad-debt risk.',
    decision: 'Denied.',
    outcome: 'Avoided ~₹3,00,000 bad-debt exposure.',
    precedents: [],
  },
  {
    id: 'EX-105', title: 'SLA service credit for downtime', customer: 'SmallCo',
    category: 'SLA', status: 'rejected', priority: 'low', amount: '₹15,000', days: 0,
    submitter: 'Ivy Chen', approver: 'Sarah Chen', created: '2026-05-25', deadline: '2026-05-28',
    reason: 'Breach traced to the customer’s own misconfiguration, not NovaFlow.',
    recommendation: 'Deny SLA credit — not a NovaFlow-caused breach.',
    decision: 'Denied with a root-cause report.',
    outcome: 'SmallCo accepted the explanation; no credit issued.',
    precedents: [],
  },
  {
    id: 'EX-106', title: 'NDA carve-out for third-party auditor', customer: 'Hooli',
    category: 'Legal', status: 'approved', priority: 'medium', amount: '—', days: 0,
    submitter: 'Sam Ortiz', approver: 'Legal (J. Rivera)', created: '2026-05-18', deadline: '2026-05-21',
    reason: 'Wants to share deliverables with a third-party auditor.',
    recommendation: 'Approve with scoped terms after legal review.',
    decision: 'Approved with scoped terms.',
    outcome: 'Deal closed; no compliance incidents.',
    precedents: [],
  },
  {
    id: 'EX-107', title: 'EU data-residency exception', customer: 'Meridian EU',
    category: 'Compliance', status: 'approved', priority: 'medium', amount: '—', days: 0,
    submitter: 'Priya Nair', approver: 'DPO (K. Adler)', created: '2026-05-15', deadline: '2026-05-18',
    reason: 'Requests data kept in-region (EU hosting).',
    recommendation: 'Approve with EU-hosting conditions (DPO sign-off).',
    decision: 'Approved under EU data-residency terms.',
    outcome: 'Onboarded successfully; compliant.',
    precedents: [],
  },
]

export const priorityText: Record<string, string> = {
  high: 'text-red-600', medium: 'text-yellow-600', low: 'text-green-600',
}
export const priorityPill: Record<string, string> = {
  high: 'bg-red-50 text-red-700 ring-1 ring-red-600/20',
  medium: 'bg-yellow-50 text-yellow-700 ring-1 ring-yellow-600/20',
  low: 'bg-green-50 text-green-700 ring-1 ring-green-600/20',
}

export const getCase = (id?: string) => DEMO_CASES.find(c => c.id === id)
export const pendingCases = () => DEMO_CASES.filter(c => c.status === 'under_review' || c.status === 'submitted')
export const decidedCases = () => DEMO_CASES.filter(c => c.status === 'approved' || c.status === 'rejected' || c.status === 'closed')

export interface DemoNotification {
  id: number; type: 'approval_needed' | 'approved' | 'rejected' | 'escalated' | 'sla'
  title: string; body: string; time: string; unread: boolean; exceptionId: string
}

export const demoNotifications = (): DemoNotification[] => {
  const notes: DemoNotification[] = []
  let i = 1
  for (const c of pendingCases()) {
    notes.push({ id: i++, type: 'approval_needed', title: 'Exception requires your approval',
      body: `${c.id}: ${c.title} for ${c.customer} (${c.amount}) is pending your decision.`,
      time: 'just now', unread: true, exceptionId: c.id })
  }
  for (const c of decidedCases().slice(0, 4)) {
    const t = c.status === 'rejected' ? 'rejected' as const : 'approved' as const
    notes.push({ id: i++, type: t, title: c.status === 'rejected' ? 'Exception rejected' : 'Exception approved',
      body: `${c.id}: ${c.title} for ${c.customer} was ${c.status}.`,
      time: 'today', unread: false, exceptionId: c.id })
  }
  return notes
}
