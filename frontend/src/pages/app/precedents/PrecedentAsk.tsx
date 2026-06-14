import { useState } from 'react'
import { Brain, Send, User } from 'lucide-react'

interface Message { role: 'user' | 'assistant'; content: string }

/** Render light markdown: **bold** becomes bold, leading #/## headers are stripped. */
function renderContent(text: string) {
  return text.split('\n').map((line, li) => {
    const clean = line.replace(/^#+\s*/, '')
    const parts = clean.split(/(\*\*[^*]+\*\*)/g)
    return (
      <div key={li}>
        {parts.map((p, i) =>
          p.startsWith('**') && p.endsWith('**')
            ? <strong key={i} className="font-semibold text-gray-900">{p.slice(2, -2)}</strong>
            : p,
        )}
      </div>
    )
  })
}

const suggestions = [
  'How have we handled emergency software procurement in the past?',
  'What is the approval rate for HR contractor rate exceptions?',
  'Show me all rejected vendor exceptions from 2024',
  'What conditions are typically attached to IT emergency approvals?',
]

export default function PrecedentAsk() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hello! I\'m your organizational memory assistant. Ask me anything about past exceptions, decisions, approval patterns, or policy trends. I have access to all precedents in your organization\'s memory.' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const send = async (text?: string) => {
    const q = text || input
    if (!q.trim()) return
    setMessages(prev => [...prev, { role: 'user', content: q }])
    setInput('')
    setLoading(true)
    await new Promise(r => setTimeout(r, 1500))
    setMessages(prev => [...prev, {
      role: 'assistant',
      content: `Based on your organizational memory, here's what I found for "${q}":\n\n**Historical Pattern:** Your organization has handled similar requests 8 times in the past 18 months. Of those, 6 were approved (75% approval rate) and 2 were rejected.\n\n**Key Precedents:**\n• PREC-0234 (Sep 2024) — Approved with 60-day limit and CISO sign-off\n• PREC-0198 (Jun 2024) — Approved with vendor security review\n• PREC-0156 (Feb 2024) — Rejected, insufficient business justification\n\n**Common Approval Conditions:**\n1. Time-limited licenses (60-90 days)\n2. CISO security sign-off required\n3. Parallel standard procurement initiated\n\n**Trend:** IT emergency exceptions have increased 31% this quarter, suggesting a potential policy update may be warranted.`
    }])
    setLoading(false)
  }

  return (
    <div className="fade-in max-w-3xl">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
          <Brain className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-gray-900">Ask Organizational Memory</h1>
          <p className="text-sm text-gray-500">Query your organization's institutional knowledge in natural language.</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-gray-200 flex flex-col" style={{ height: 520 }}>
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`flex gap-3 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 ${m.role === 'assistant' ? 'bg-primary/20' : 'bg-gray-100'}`}>
                {m.role === 'assistant' ? <Brain className="w-3.5 h-3.5 text-primary" /> : <User className="w-3.5 h-3.5 text-gray-600" />}
              </div>
              <div className={`max-w-lg rounded-2xl px-4 py-3 text-sm leading-relaxed space-y-1 ${m.role === 'assistant' ? 'bg-gray-50 text-gray-700 rounded-tl-none' : 'bg-primary/20 text-gray-900 rounded-tr-none'}`}>
                {m.role === 'assistant' ? renderContent(m.content) : m.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center"><Brain className="w-3.5 h-3.5 text-primary" /></div>
              <div className="bg-gray-50 rounded-2xl rounded-tl-none px-4 py-3 flex gap-1.5">
                {[0.1, 0.2, 0.3].map(d => <div key={d} className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: `${d}s` }} />)}
              </div>
            </div>
          )}
        </div>

        {/* Suggestions */}
        {messages.length <= 1 && (
          <div className="px-4 pb-3 flex flex-wrap gap-2">
            {suggestions.map(s => (
              <button key={s} onClick={() => send(s)}
                className="text-xs text-gray-500 border border-gray-200 rounded-lg px-3 py-1.5 hover:border-primary/30 hover:text-gray-900 transition-all bg-gray-50">
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="p-4 border-t border-gray-200 flex gap-2">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
            placeholder="Ask about precedents, patterns, decisions..."
            className="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all"
          />
          <button onClick={() => send()} disabled={!input.trim() || loading}
            className="p-2.5 rounded-xl bg-primary hover:bg-primary-dark text-white transition-colors disabled:opacity-50">
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
