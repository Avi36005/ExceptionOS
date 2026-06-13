interface Props { children: React.ReactNode; className?: string; onClick?: () => void }
export default function Card({ children, className = '', onClick }: Props) {
  return (
    <div
      className={`bg-dark2 rounded-xl border border-white/10 p-6 ${onClick ? 'cursor-pointer hover:border-primary/30 transition-colors' : ''} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  )
}
