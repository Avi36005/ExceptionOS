interface Props { size?: 'sm' | 'md' | 'lg' }
export default function LoadingSpinner({ size = 'md' }: Props) {
  const s = size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-12 h-12' : 'w-8 h-8'
  return (
    <div className={`${s} border-2 border-primary/20 border-t-primary rounded-full animate-spin`} />
  )
}
