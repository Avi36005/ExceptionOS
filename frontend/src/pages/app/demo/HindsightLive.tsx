import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Brain, Send, Zap } from 'lucide-react'

const demoAnswers: Record<string, string> = {
  default: 'Based on 284 precedents in your organizational memory, here\'s what I found:\n\n**Approval Rate:** 78% for this type of exception\n**Common Conditions:** Time limits, security review, parallel procurement\n**Trend:** Volume up 31% this quarter\n\nWould you like me to find the 3 most similar past decisions?'
}

export default function HindsightLive() {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)

  const runQuery = async () => {
    if (!query) return
    setLoading(true)
    setResult('')
    await new Promise(r => setTimeout(r, 2000))
    setResult(demoAnswers.default)
    setLoading(false)
  }

  const sampleQueries = [
    'How have we handled emergency software exceptions?',
    'What is our approval rate for HR contractor exceptions?',
    'Show me patterns in Q4 exceptions',
  ]

  return (
    <div className="min-h-screen bg-dark flex flex-col items-center justify-center p-6">
      <button onClick={() => navigate('/demo')} className="absolute top-6 left-6 flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back
      </button>
      <div className="max-w-2xl w-full">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
            <Brain className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Hindsight™ Live Demo</h1>
          <p className="text-gray-400">Query organizational memory in natural language. No account needed.</p>
        </div>

        <div className="bg-dark2 rounded-2xl border border-white/10 p-6 mb-4">
          <div className="flex gap-2 mb-4">
            <input value={query} onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && runQuery()}
              placeholder="Ask anything about past decisions..."
              className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary/60 transition-all" />
            <button onClick={runQuery} disabled={!query || loading}
              className="p-2.5 rounded-xl bg-primary hover:bg-primary-dark text-white transition-colors disabled:opacity-50">
              <Send className="w-4 h-4" />
            </button>
          </div>

          {!query && (
            <div className="flex flex-wrap gap-2">
              {sampleQueries.map(q => (
                <button key={q} onClick={() => setQuery(q)} className="text-xs text-gray-400 border border-white/10 rounded-lg px-3 py-1.5 hover:border-primary/30 hover:text-white transition-all bg-white/3">
                  {q}
                </button>
              ))}
            </div>
          )}

          {loading && (
            <div className="flex items-center gap-3 fade-in">
              <div className="flex gap-1">
                {[0, 0.2, 0.4].map(d => <div key={d} className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: `${d}s` }} />)}
              </div>
              <span className="text-sm text-gray-400">Querying organizational memory...</span>
            </div>
          )}

          {result && (
            <div className="bg-primary/5 border border-primary/20 rounded-xl p-4 fade-in">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="w-4 h-4 text-primary" />
                <span className="text-xs font-semibold text-primary">Hindsight™ Response</span>
              </div>
              <p className="text-sm text-gray-300 whitespace-pre-line leading-relaxed">{result}</p>
            </div>
          )}
        </div>

        <p className="text-center text-xs text-gray-500">
          This demo uses synthetic data. <button onClick={() => navigate('/signup')} className="text-primary hover:underline">Sign up free</button> to use your real organizational data.
        </p>
      </div>
    </div>
  )
}
