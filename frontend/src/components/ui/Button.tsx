import { Loader2 } from 'lucide-react'
type Variant = 'primary' | 'secondary' | 'danger' | 'ghost'
type Size = 'sm' | 'md' | 'lg'
interface Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant; size?: Size; loading?: boolean; icon?: React.ReactNode
}
export default function Button({ children, variant = 'primary', size = 'md', loading, icon, className = '', disabled, ...props }: Props) {
  const variants = {
    primary: 'bg-primary hover:bg-primary-dark text-white shadow-[0_4px_14px_rgba(91,91,240,.25)]',
    secondary: 'bg-white hover:bg-gray-50 text-gray-700 border border-gray-200',
    danger: 'bg-red-600 hover:bg-red-700 text-white',
    ghost: 'text-gray-500 hover:text-gray-900 hover:bg-gray-100',
  }
  const sizes = { sm: 'px-3 py-1.5 text-xs', md: 'px-4 py-2 text-sm', lg: 'px-6 py-3 text-base' }
  return (
    <button
      className={`inline-flex items-center gap-2 rounded-lg font-medium transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : icon}
      {children}
    </button>
  )
}
