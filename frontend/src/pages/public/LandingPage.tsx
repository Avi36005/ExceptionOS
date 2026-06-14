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
    <div className="min-h-screen bg-white text-gray-900 font-sans">
      {/* Nav */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-white/80 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-[#7C5CFF] flex items-center justify-center shadow-[0_4px_14px_rgba(91,91,240,.4)]">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-gray-900 text-lg tracking-tight">ExceptionOS</span>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => navigate('/login')} className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors px-4 py-2">
              Sign in
            </button>
            <button
              onClick={() => navigate('/signup')}
              className="text-sm px-4 py-2 rounded-full bg-primary hover:bg-primary-dark text-white font-semibold transition-all hover:-translate-y-0.5 shadow-[0_6px_18px_rgba(91,91,240,.35)] flex items-center gap-2"
            >
              Get started free <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </nav>

      {/* Hero — dark, with radial purple glow (Orbiz-style) */}
      <section
        className="relative overflow-hidden text-center px-6 pt-28 pb-32"
        style={{
          background:
            'radial-gradient(ellipse 70% 60% at 50% 115%, rgba(88,60,255,.55) 0%, rgba(55,35,180,.22) 42%, transparent 68%), linear-gradient(180deg,#08090f 0%,#0b0b1f 100%)',
        }}
      >
        <div className="absolute bottom-[-60px] left-1/2 -translate-x-1/2 w-[800px] h-[500px] pointer-events-none"
          style={{ background: 'radial-gradient(ellipse at 50% 100%, rgba(100,70,255,.4) 0%, transparent 68%)' }}
        />
        <div className="relative max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/[0.06] border border-white/10 text-white/80 text-xs font-medium mb-8">
            <span className="bg-primary text-white text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wide">New</span>
            Multi-tenant organizational decision intelligence
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold text-white mb-6 leading-[1.05] tracking-tight">
            When policy ends,<br />
            <span className="bg-gradient-to-r from-[#8B8BFF] to-primary bg-clip-text text-transparent">memory begins.</span>
          </h1>
          <p className="text-lg text-white/55 max-w-2xl mx-auto mb-10 leading-relaxed">
            ExceptionOS is the intelligent platform that manages policy exceptions, builds institutional memory,
            and ensures every decision is consistent, defensible, and auditable.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onClick={() => navigate('/signup')}
              className="flex items-center justify-center gap-2 px-8 py-4 rounded-full bg-primary hover:bg-primary-dark text-white font-semibold text-base transition-all hover:-translate-y-0.5 shadow-[0_10px_30px_rgba(91,91,240,.45)]"
            >
              Start for free <ArrowRight className="w-5 h-5" />
            </button>
            <button
              onClick={() => navigate('/demo')}
              className="flex items-center justify-center gap-2 px-8 py-4 rounded-full bg-white/[0.08] hover:bg-white/[0.14] text-white font-semibold text-base transition-colors border border-white/15"
            >
              Watch demo
            </button>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-6 mt-12 text-sm text-white/45">
            {['No credit card required', 'Free 30-day trial', 'SOC 2 compliant'].map(t => (
              <div key={t} className="flex items-center gap-1.5">
                <CheckCircle className="w-4 h-4 text-green-400" />
                {t}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features — light section */}
      <section className="py-24 px-6 bg-light">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-1.5 text-xs font-bold text-primary uppercase tracking-wider mb-3">
              ✦ Features
            </div>
            <h2 className="text-3xl md:text-5xl font-extrabold italic text-gray-900 mb-4 tracking-tight">Everything you need for<br />exception management</h2>
            <p className="text-gray-500 max-w-xl mx-auto">Built for enterprises that need consistency, auditability, and intelligence at every decision point.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {features.map(f => (
              <div key={f.title} className="group bg-white rounded-2xl border border-gray-200 p-7 shadow-card hover:shadow-card-hover hover:-translate-y-1.5 hover:border-primary/20 transition-all">
                <div className="w-11 h-11 rounded-xl bg-primary/10 flex items-center justify-center mb-5">
                  <f.icon className="w-5 h-5 text-primary" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials — white section */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-1.5 text-xs font-bold text-primary uppercase tracking-wider mb-3">
              ✦ Testimonials
            </div>
            <h2 className="text-3xl md:text-5xl font-extrabold italic text-gray-900 tracking-tight">Trusted by leading organizations</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {testimonials.map(t => (
              <div key={t.name} className="bg-light rounded-2xl border border-gray-200 p-7 hover:shadow-card-hover hover:-translate-y-1 transition-all">
                <div className="flex gap-1 mb-4">
                  {[...Array(5)].map((_, i) => <Star key={i} className="w-4 h-4 text-amber-400 fill-amber-400" />)}
                </div>
                <p className="text-gray-700 text-sm leading-relaxed mb-6">"{t.text}"</p>
                <div>
                  <div className="text-sm font-bold text-gray-900">{t.name}</div>
                  <div className="text-xs text-gray-500">{t.role}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA — dark band */}
      <section className="py-20 px-6 bg-light">
        <div
          className="max-w-4xl mx-auto text-center rounded-3xl p-14 relative overflow-hidden"
          style={{ background: 'linear-gradient(135deg,#0c0f24 0%,#15123a 100%)' }}
        >
          <div className="absolute -top-24 -left-24 w-72 h-72 rounded-full pointer-events-none"
            style={{ background: 'radial-gradient(ellipse,rgba(91,91,240,.25) 0%,transparent 70%)' }}
          />
          <h2 className="relative text-3xl md:text-4xl font-extrabold italic text-white mb-4 tracking-tight">Ready to transform how your<br />organization handles exceptions?</h2>
          <p className="relative text-white/55 mb-8">Join hundreds of organizations building defensible decision processes.</p>
          <button
            onClick={() => navigate('/signup')}
            className="relative flex items-center justify-center gap-2 px-8 py-4 rounded-full bg-primary hover:bg-primary-dark text-white font-semibold text-base transition-all hover:-translate-y-0.5 shadow-[0_10px_30px_rgba(91,91,240,.45)] mx-auto"
          >
            Get started free <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </section>

      {/* Footer — dark */}
      <footer className="py-10 px-6" style={{ background: '#060916' }}>
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
              <Zap className="w-3 h-3 text-white" />
            </div>
            <span className="text-sm font-semibold text-white">ExceptionOS</span>
          </div>
          <p className="text-xs text-white/40">© 2024 ExceptionOS. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
