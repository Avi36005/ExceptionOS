import { useNavigate } from 'react-router-dom'
import { ArrowRight, Zap, Shield, Brain, BarChart3, CheckCircle, Star } from 'lucide-react'

const features = [
  { icon: Brain, title: 'AI-Powered Decision Intelligence', desc: 'Every exception request is analyzed by AI against your policies and historical precedents for consistent, defensible decisions.' },
  { icon: Shield, title: 'Policy Management', desc: 'Maintain a living library of organizational policies with version control, drift detection, and compliance simulation.' },
  { icon: BarChart3, title: 'Precedent Memory', desc: 'Build institutional knowledge from every decision. Query your organization\'s decision history in natural language.' },
  { icon: Zap, title: 'Automated Workflows', desc: 'Route exceptions through the right approval chains automatically based on category, risk level, and department.' },
]

const testimonials = [
  { name: 'Sarah Chen', role: 'VP Operations, TechCorp', text: 'ExceptionOS reduced our exception processing time by 70%. The AI recommendations are consistently on-point.' },
  { name: 'Marcus Williams', role: 'CFO, Global Finance Inc', text: 'We finally have a defensible audit trail for every exception decision. Our compliance team loves it.' },
  { name: 'Priya Patel', role: 'Head of HR, StartupCo', text: 'The precedent memory feature is a game-changer. New managers can make consistent decisions from day one.' },
]

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-dark text-light font-sans">
      {/* Nav */}
      <nav className="border-b border-white/10 backdrop-blur-sm sticky top-0 z-50 bg-dark/80">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-white text-lg">ExceptionOS</span>
          </div>
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/login')} className="text-sm text-gray-400 hover:text-white transition-colors px-4 py-2">
              Sign in
            </button>
            <button
              onClick={() => navigate('/signup')}
              className="btn-primary text-sm px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white font-medium transition-colors flex items-center gap-2"
            >
              Get started free <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative py-24 px-6 text-center overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-primary/5 rounded-full blur-3xl" />
        </div>
        <div className="relative max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-medium mb-6">
            <Star className="w-3 h-3" /> Multi-tenant organizational decision intelligence
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
            When policy ends,<br />
            <span className="text-primary">memory begins.</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
            ExceptionOS is the intelligent platform that manages policy exceptions, builds institutional memory,
            and ensures every decision is consistent, defensible, and auditable.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/signup')}
              className="flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold text-lg transition-colors"
            >
              Start for free <ArrowRight className="w-5 h-5" />
            </button>
            <button
              onClick={() => navigate('/demo')}
              className="flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-white/10 hover:bg-white/15 text-white font-semibold text-lg transition-colors border border-white/10"
            >
              Watch demo
            </button>
          </div>
          <div className="flex items-center justify-center gap-6 mt-12 text-sm text-gray-500">
            {['No credit card required', 'Free 30-day trial', 'SOC 2 compliant'].map(t => (
              <div key={t} className="flex items-center gap-1.5">
                <CheckCircle className="w-4 h-4 text-green-500" />
                {t}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Everything you need for exception management</h2>
            <p className="text-gray-400 max-w-xl mx-auto">Built for enterprises that need consistency, auditability, and intelligence at every decision point.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map(f => (
              <div key={f.title} className="bg-dark2 rounded-2xl border border-white/10 p-6 hover:border-primary/30 transition-colors">
                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                  <f.icon className="w-5 h-5 text-primary" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{f.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-6 border-t border-white/10">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Trusted by leading organizations</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {testimonials.map(t => (
              <div key={t.name} className="bg-dark2 rounded-2xl border border-white/10 p-6">
                <div className="flex gap-1 mb-4">
                  {[...Array(5)].map((_, i) => <Star key={i} className="w-4 h-4 text-yellow-400 fill-yellow-400" />)}
                </div>
                <p className="text-gray-300 text-sm leading-relaxed mb-6">"{t.text}"</p>
                <div>
                  <div className="text-sm font-semibold text-white">{t.name}</div>
                  <div className="text-xs text-gray-500">{t.role}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6">
        <div className="max-w-3xl mx-auto text-center bg-dark2 rounded-3xl border border-primary/20 p-12">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to transform how your organization handles exceptions?</h2>
          <p className="text-gray-400 mb-8">Join hundreds of organizations building defensible decision processes.</p>
          <button
            onClick={() => navigate('/signup')}
            className="flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold text-lg transition-colors mx-auto"
          >
            Get started free <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8 px-6">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
              <Zap className="w-3 h-3 text-white" />
            </div>
            <span className="text-sm font-semibold text-white">ExceptionOS</span>
          </div>
          <p className="text-xs text-gray-500">© 2024 ExceptionOS. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
