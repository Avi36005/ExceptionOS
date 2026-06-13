interface Column<T> { key: keyof T | string; header: string; render?: (row: T) => React.ReactNode }
interface Props<T> { columns: Column<T>[]; data: T[]; loading?: boolean; emptyMessage?: string }
export default function Table<T extends Record<string, unknown>>({ columns, data, loading, emptyMessage = 'No data found' }: Props<T>) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/10">
            {columns.map(col => (
              <th key={String(col.key)} className="text-left py-3 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">{col.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {loading ? (
            Array.from({ length: 5 }).map((_, i) => (
              <tr key={i} className="border-b border-white/5">
                {columns.map((_, j) => <td key={j} className="py-3 px-4"><div className="h-4 bg-white/5 rounded shimmer" /></td>)}
              </tr>
            ))
          ) : data.length === 0 ? (
            <tr><td colSpan={columns.length} className="py-12 text-center text-gray-500">{emptyMessage}</td></tr>
          ) : (
            data.map((row, i) => (
              <tr key={i} className="border-b border-white/5 hover:bg-white/2 transition-colors">
                {columns.map(col => (
                  <td key={String(col.key)} className="py-3 px-4 text-gray-300">
                    {col.render ? col.render(row) : String(row[col.key as keyof T] ?? '')}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
