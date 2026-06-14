import { Tag, Plus } from 'lucide-react'

const categories = [
  { id: '1', name: 'IT & Security', color: '#5B5BF0', exceptions: 31, policies: 4, active: true },
  { id: '2', name: 'HR & Employment', color: '#22c55e', exceptions: 18, policies: 3, active: true },
  { id: '3', name: 'Vendor & Procurement', color: '#f59e0b', exceptions: 24, policies: 5, active: true },
  { id: '4', name: 'Finance & Compliance', color: '#ef4444', exceptions: 15, policies: 3, active: true },
  { id: '5', name: 'Legal & Contracts', color: '#8b5cf6', exceptions: 9, policies: 2, active: true },
  { id: '6', name: 'Operations', color: '#06b6d4', exceptions: 8, policies: 2, active: false },
]

export default function Categories() {
  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Tag className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold text-gray-900">Exception Categories</h1>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" /> Add Category
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {categories.map(c => (
          <div key={c.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:border-gray-300 cursor-pointer transition-all">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: c.color }} />
              <h3 className="text-sm font-semibold text-gray-900 flex-1">{c.name}</h3>
              <span className={`w-2 h-2 rounded-full ${c.active ? 'bg-green-500' : 'bg-gray-300'}`} />
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs text-gray-500">
              <div><span className="text-gray-900 font-semibold text-sm">{c.exceptions}</span> exceptions</div>
              <div><span className="text-gray-900 font-semibold text-sm">{c.policies}</span> policies</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
