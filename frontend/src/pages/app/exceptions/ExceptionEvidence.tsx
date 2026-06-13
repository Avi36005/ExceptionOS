import { FileText, Download, Eye, Upload, CheckCircle } from 'lucide-react'

const evidence = [
  { id: 1, name: 'Vendor_Quote_Figma_Enterprise.pdf', type: 'PDF', size: '245 KB', uploaded: '2024-12-18', verified: true },
  { id: 2, name: 'Project_Timeline_Q1_Launch.xlsx', type: 'Excel', size: '128 KB', uploaded: '2024-12-18', verified: true },
  { id: 3, name: 'Revenue_Impact_Analysis.docx', type: 'Word', size: '89 KB', uploaded: '2024-12-18', verified: false },
  { id: 4, name: 'Stakeholder_Approval_Email.pdf', type: 'PDF', size: '67 KB', uploaded: '2024-12-18', verified: true },
]

const typeColors: Record<string, string> = {
  PDF: 'bg-red-500/20 text-red-400',
  Excel: 'bg-green-500/20 text-green-400',
  Word: 'bg-blue-500/20 text-blue-400',
}

export default function ExceptionEvidence() {
  return (
    <div className="fade-in space-y-6">
      <div className="bg-dark2 rounded-xl border border-white/10 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-white">Supporting Documents</h3>
          <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary/10 hover:bg-primary/20 text-primary text-sm font-medium transition-colors">
            <Upload className="w-4 h-4" /> Upload
          </button>
        </div>
        <div className="space-y-2">
          {evidence.map(e => (
            <div key={e.id} className="flex items-center gap-4 p-3 bg-white/5 rounded-lg border border-white/5 hover:border-white/10 transition-colors">
              <div className={`px-2 py-0.5 rounded text-xs font-medium shrink-0 ${typeColors[e.type] || 'bg-gray-500/20 text-gray-400'}`}>{e.type}</div>
              <div className="flex-1 min-w-0">
                <div className="text-sm text-white font-medium truncate">{e.name}</div>
                <div className="text-xs text-gray-500 mt-0.5">{e.size} · Uploaded {e.uploaded}</div>
              </div>
              {e.verified && (
                <div className="flex items-center gap-1 text-xs text-green-400">
                  <CheckCircle className="w-3.5 h-3.5" /> Verified
                </div>
              )}
              <div className="flex items-center gap-1">
                <button className="p-1.5 rounded hover:bg-white/10 text-gray-400 hover:text-white transition-colors"><Eye className="w-4 h-4" /></button>
                <button className="p-1.5 rounded hover:bg-white/10 text-gray-400 hover:text-white transition-colors"><Download className="w-4 h-4" /></button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="border-2 border-dashed border-white/10 rounded-xl p-8 text-center hover:border-primary/30 transition-colors cursor-pointer">
        <FileText className="w-8 h-8 text-gray-600 mx-auto mb-3" />
        <p className="text-sm text-gray-400 font-medium">Drop files here to upload</p>
        <p className="text-xs text-gray-600 mt-1">PDF, DOC, XLS, PNG, JPG up to 10MB each</p>
      </div>
    </div>
  )
}
