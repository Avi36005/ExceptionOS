import { ChevronDown } from 'lucide-react'
interface Option { value: string; label: string }
interface Props { label?: string; options: Option[]; value: string; onChange: (v: string) => void; placeholder?: string }
export default function Select({ label, options, value, onChange, placeholder }: Props) {
  return (
    <div className="w-full">
      {label && <label className="block text-sm font-medium text-gray-300 mb-1.5">{label}</label>}
      <div className="relative">
        <select
          value={value}
          onChange={e => onChange(e.target.value)}
          className="w-full appearance-none bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/30 transition-all pr-8"
        >
          {placeholder && <option value="">{placeholder}</option>}
          {options.map(o => <option key={o.value} value={o.value} className="bg-dark2">{o.label}</option>)}
        </select>
        <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
      </div>
    </div>
  )
}
