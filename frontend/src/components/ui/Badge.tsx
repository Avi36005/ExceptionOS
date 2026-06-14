type Variant = 'default' | 'success' | 'warning' | 'danger' | 'info' | 'purple'
interface Props { children: React.ReactNode; variant?: Variant; className?: string }
export default function Badge({ children, variant = 'default', className = '' }: Props) {
  const variants = {
    default: 'bg-gray-100 text-gray-600',
    success: 'bg-green-50 text-green-700 ring-1 ring-green-200',
    warning: 'bg-amber-50 text-amber-700 ring-1 ring-amber-200',
    danger: 'bg-red-50 text-red-700 ring-1 ring-red-200',
    info: 'bg-blue-50 text-blue-700 ring-1 ring-blue-200',
    purple: 'bg-primary/10 text-primary ring-1 ring-primary/20',
  }
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium ${variants[variant]} ${className}`}>
      {children}
    </span>
  )
}
