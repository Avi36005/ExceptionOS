import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Brain, Filter, CheckCircle, XCircle, Network } from 'lucide-react'

const precedents = [
  { id: 'PREC-0234', title: 'Emergency Figma licenses for product launch', category: 'IT', decision: 'approved', date: '2024-09-12', tags: ['Emergency', 'SaaS', 'Design'] },
  { id: 'PREC-0198', title: 'Adobe Creative Suite emergency procurement', category: 'IT', decision: 'approved', date: '2024-06-03', tags: ['Emergency', 'Creative', 'SaaS'] },
  { id: 'PREC-0187', title: 'Contractor rate exception for senior engineer', category: 'HR', decision: 'approved', date: '2024-05-15', tags: ['Contractor', 'Engineering', 'Rate'] },
  { id: 'PREC-0175', title: 'Sole-source vendor for proprietary system', category: 'Vendor', decision: 'approved', date: '2024-04-02', tags: ['Sole-source', 'Proprietary'] },
  { id: 'PREC-0156', title: 'Slack enterprise upgrade outside procurement', category: 'IT', decision: 'rejected', date: '2024-02-14', tags: ['SaaS', 'Procurement'] },
  { id: 'PREC-0142', title: 'Zoom Webinar license emergency', category: 'IT', decision: 'approved', date: '2023-11-28', tags: ['Emergency', 'SaaS', 'Events'] },
  { id: 'PREC-0128', title: 'Remote employee relocation assistance', category: 'HR', decision: 'approved', date: '2023-09-10', tags: ['Remote', 'Relocation', 'HR'] },
  { id: 'PREC-0099', title: 'Budget carryover from Q2 to Q3', category: 'Finance', decision: 'rejected', date: '2023-07-01', tags: ['Budget', 'Carryover'] },
]

export default function PrecedentSearch() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('all')
  const [decision, setDecision] = useState('all')

  const categories = ['all', 'IT', 'HR', 'Vendor', 'Finance', 'Legal']

  const filtered = precedents
    .filter(p => category === 'all' || p.category === category)
    .filter(p => decision === 'all' || p.decision === decision)
    .filter(p => !search || p.title.toLowerCase().includes(search.toLowerCase()) || p.tags.some(t => t.toLowerCase().includes(search.toLowerCase())))

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Precedent Library</h1>
          <p className="text-sm text-gray-500 mt-1">{precedents.length} precedents in organizational memory</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => navigate('/app/precedents/ask')} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-100 text-gray-900 text-sm font-medium border border-gray-200 transition-colors">
            <Brain className="w-4 h-4" /> Ask AI
          </button>
          <button onClick={() => navigate('/app/precedents/graph')} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-100 text-gray-900 text-sm font-medium border border-gray-200 transition-colors">
            <Network className="w-4 h-4" /> Graph
          </button>
        </div>
      </div>

      <div className="flex items-center gap-3 mb-4 flex-wrap">
        <div className="relative flex-1 min-w-60">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search precedents by title, tags, or keywords..."
            className="w-full bg-gray-50 border border-gray-200 rounded-lg pl-9 pr-3 py-2 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
        </div>
        <div className="flex gap-1">
          {categories.map(c => (
            <button key={c} onClick={() => setCategory(c)}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${category === c ? 'bg-primary/20 text-primary border border-primary/30' : 'bg-gray-50 text-gray-500 hover:text-gray-900 border border-gray-200'}`}>
              {c === 'all' ? 'All' : c}
            </button>
          ))}
        </div>
        <div className="flex gap-1">
          {[['all', 'All'], ['approved', 'Approved'], ['rejected', 'Rejected']].map(([val, label]) => (
            <button key={val} onClick={() => setDecision(val)}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${decision === val ? 'bg-primary/20 text-primary border border-primary/30' : 'bg-gray-50 text-gray-500 hover:text-gray-900 border border-gray-200'}`}>
              {label}
            </button>
          ))}
        </div>
        <button className="p-2 rounded-lg bg-gray-50 border border-gray-200 text-gray-500 hover:text-gray-900 transition-colors">
          <Filter className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-3">
        {filtered.map(p => (
          <div key={p.id} className="bg-white rounded-xl border border-gray-200 p-4 hover:border-primary/30 cursor-pointer transition-all"
            onClick={() => navigate(`/app/precedents/${p.id}`)}>
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-mono text-gray-500">{p.id}</span>
                  <span className="text-xs text-gray-600">·</span>
                  <span className="text-xs text-gray-500">{p.category}</span>
                  <span className="text-xs text-gray-600">·</span>
                  <span className="text-xs text-gray-500">{p.date}</span>
                </div>
                <h3 className="text-sm font-semibold text-gray-900 mb-2">{p.title}</h3>
                <div className="flex flex-wrap gap-1.5">
                  {p.tags.map(tag => (
                    <span key={tag} className="px-2 py-0.5 rounded-md text-xs bg-gray-50 text-gray-500 border border-gray-100">{tag}</span>
                  ))}
                </div>
              </div>
              <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium shrink-0 ring-1 ${p.decision === 'approved' ? 'bg-green-50 text-green-700 ring-green-600/20' : 'bg-red-50 text-red-700 ring-red-600/20'}`}>
                {p.decision === 'approved' ? <CheckCircle className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                {p.decision.charAt(0).toUpperCase() + p.decision.slice(1)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
