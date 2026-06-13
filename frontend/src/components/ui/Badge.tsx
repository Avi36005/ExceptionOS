type Variant = 'default' | 'success' | 'warning' | 'danger' | 'info' | 'purple'
interface Props { children: React.ReactNode; variant?: Variant; className?: string }
export default function Badge({ children, variant = 'default', className = '' }: Props) {
  const variants = {
    default: 'bg-white/10 text-gray-300',
    success: 'bg-green-500/20 text-green-400',
    warning: 'bg-yellow-500/20 text-yellow-400',
    danger: 'bg-red-500/20 text-red-400',
    info: 'bg-blue-500/20 text-blue-400',
    purple: 'bg-primary/20 text-primary',
  }
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium ${variants[variant]} ${className}`}>
      {children}
    </span>
  )
}
