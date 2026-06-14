interface Props { children: React.ReactNode; className?: string; onClick?: () => void }
export default function Card({ children, className = '', onClick }: Props) {
  return (
    <div
      className={`bg-white rounded-xl border border-gray-200 shadow-card p-6 ${onClick ? 'cursor-pointer hover:border-primary/30 hover:shadow-card-hover transition-all' : ''} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  )
}
