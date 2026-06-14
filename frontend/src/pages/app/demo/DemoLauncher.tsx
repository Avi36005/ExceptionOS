import { useNavigate } from 'react-router-dom'
import { Zap, Play, Brain, ArrowLeft, Star } from 'lucide-react'

export default function DemoLauncher() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-light flex flex-col items-center justify-center p-6">
      <button onClick={() => navigate('/')} className="absolute top-6 left-6 flex items-center gap-2 text-sm text-gray-500 hover:text-gray-900 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      <div className="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center mb-6">
        <Zap className="w-8 h-8 text-white" />
      </div>
      <h1 className="text-3xl font-bold text-gray-900 mb-3 text-center">ExceptionOS Interactive Demo</h1>
      <p className="text-gray-500 text-center max-w-xl mb-10">Experience the full power of organizational decision intelligence. No account required.</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl w-full mb-8">
        {[
          { icon: Play, title: 'Full Story Demo', desc: 'Walk through a complete exception lifecycle with AI analysis, debate, and decision.', to: '/demo/story', featured: true },
          { icon: Brain, title: 'Hindsight™ Live', desc: 'See the AI memory engine query institutional knowledge in real-time.', to: '/demo/hindsight-live', featured: false },
          { icon: Star, title: 'Before vs. After', desc: 'Compare how organizations operate without and with ExceptionOS.', to: '/demo/before-after', featured: false },
        ].map(d => (
          <button key={d.title} onClick={() => navigate(d.to)}
            className={`p-5 rounded-2xl border text-left hover:border-primary/40 transition-all ${d.featured ? 'bg-primary/10 border-primary/30' : 'bg-white border-gray-200'}`}>
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center mb-3">
              <d.icon className="w-5 h-5 text-primary" />
            </div>
            <h3 className="text-sm font-semibold text-gray-900 mb-1">{d.title}</h3>
            <p className="text-xs text-gray-500 leading-relaxed">{d.desc}</p>
          </button>
        ))}
      </div>

      <p className="text-xs text-gray-600 text-center">Or <button onClick={() => navigate('/signup')} className="text-primary hover:underline">create a free account</button> to get started with real data.</p>
    </div>
  )
}
