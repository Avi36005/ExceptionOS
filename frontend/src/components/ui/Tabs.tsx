interface Tab { id: string; label: string; icon?: React.ReactNode }
interface Props { tabs: Tab[]; active: string; onChange: (id: string) => void }
export default function Tabs({ tabs, active, onChange }: Props) {
  return (
    <div className="flex items-center gap-1 border-b border-gray-200 overflow-x-auto">
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-all ${
            active === tab.id
              ? 'border-primary text-primary'
              : 'border-transparent text-gray-500 hover:text-gray-900'
          }`}
        >
          {tab.icon}{tab.label}
        </button>
      ))}
    </div>
  )
}
