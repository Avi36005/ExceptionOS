import { ChevronRight, Home } from 'lucide-react'
import { Link } from 'react-router-dom'

interface Crumb { label: string; to?: string }
interface Props { crumbs: Crumb[] }

export default function Breadcrumbs({ crumbs }: Props) {
  return (
    <nav className="flex items-center gap-1 text-sm mb-6">
      <Link to="/app" className="text-gray-500 hover:text-white transition-colors">
        <Home className="w-4 h-4" />
      </Link>
      {crumbs.map((crumb, i) => (
        <div key={i} className="flex items-center gap-1">
          <ChevronRight className="w-3 h-3 text-gray-600" />
          {crumb.to && i < crumbs.length - 1 ? (
            <Link to={crumb.to} className="text-gray-400 hover:text-white transition-colors">{crumb.label}</Link>
          ) : (
            <span className="text-gray-300">{crumb.label}</span>
          )}
        </div>
      ))}
    </nav>
  )
}
