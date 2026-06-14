import { useNavigate } from 'react-router-dom'
import { GraduationCap, Clock, Star, Play } from 'lucide-react'

const scenarios = [
  { id: 'SCN-001', title: 'When to Approve an Emergency Exception', category: 'Decision Making', difficulty: 'Beginner', duration: '15 min', rating: 4.8, completions: 234 },
  { id: 'SCN-002', title: 'Detecting Policy Gaming Patterns', category: 'Compliance', difficulty: 'Intermediate', duration: '25 min', rating: 4.6, completions: 156 },
  { id: 'SCN-003', title: 'Writing Strong Decision Rationale', category: 'Communication', difficulty: 'Beginner', duration: '20 min', rating: 4.9, completions: 312 },
  { id: 'SCN-004', title: 'Escalation Decision Framework', category: 'Decision Making', difficulty: 'Advanced', duration: '30 min', rating: 4.7, completions: 98 },
  { id: 'SCN-005', title: 'Vendor Exception Best Practices', category: 'Vendor', difficulty: 'Intermediate', duration: '20 min', rating: 4.5, completions: 187 },
  { id: 'SCN-006', title: 'Maintaining Decision Consistency', category: 'Compliance', difficulty: 'Advanced', duration: '35 min', rating: 4.8, completions: 76 },
]

const diffColors: Record<string, string> = {
  Beginner: 'bg-green-50 text-green-700 ring-1 ring-green-600/20',
  Intermediate: 'bg-yellow-50 text-yellow-700 ring-1 ring-yellow-600/20',
  Advanced: 'bg-red-50 text-red-700 ring-1 ring-red-600/20',
}

export default function TrainingLibrary() {
  const navigate = useNavigate()

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <GraduationCap className="w-6 h-6 text-primary" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Training Library</h1>
            <p className="text-sm text-gray-500 mt-1">Interactive scenarios to improve exception decision-making skills.</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {scenarios.map(s => (
          <div key={s.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:border-primary/30 transition-all cursor-pointer"
            onClick={() => navigate(`/app/training/${s.id}`)}>
            <div className="flex items-center justify-between mb-3">
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${diffColors[s.difficulty]}`}>{s.difficulty}</span>
              <span className="text-xs text-gray-500">{s.category}</span>
            </div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3 leading-snug">{s.title}</h3>
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{s.duration}</span>
              <span className="flex items-center gap-1"><Star className="w-3 h-3 text-yellow-500" />{s.rating}</span>
              <span>{s.completions} completions</span>
            </div>
            <button className="w-full mt-4 flex items-center justify-center gap-2 py-2 rounded-lg bg-primary/10 hover:bg-primary/20 text-primary text-xs font-medium transition-colors">
              <Play className="w-3.5 h-3.5" /> Start Training
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
