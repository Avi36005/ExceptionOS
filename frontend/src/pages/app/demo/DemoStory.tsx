import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Zap, CheckCircle } from 'lucide-react'

const steps = [
  { title: 'Exception Submitted', desc: 'Alex from Design submits an emergency exception for Figma Enterprise licenses — needed in 5 days for a board presentation.' },
  { title: 'AI Policy Analysis', desc: 'Hindsight™ instantly checks 3 relevant policies. Identifies 1 violation, 1 partial conflict, and an applicable emergency provision.' },
  { title: 'Precedent Search', desc: 'AI finds 4 similar cases from your memory — 3 approved, 1 rejected. Approval pattern is 82% for this type of request.' },
  { title: 'Adversarial Debate', desc: 'AI generates 4 arguments for and 3 arguments against approval, helping the decision-maker see all angles.' },
  { title: 'Decision Made', desc: 'Approver reviews all context and approves with 4 conditions. Entire process took 6 hours 40 minutes.' },
  { title: 'Memory Committed', desc: 'The decision is added to organizational memory. Future similar requests will automatically reference this precedent.' },
]

export default function DemoStory() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)

  return (
    <div className="min-h-screen bg-light flex flex-col items-center justify-center p-6">
      <button onClick={() => navigate('/demo')} className="absolute top-6 left-6 flex items-center gap-2 text-sm text-gray-500 hover:text-gray-900 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back to demos
      </button>

      <div className="max-w-2xl w-full">
        <div className="flex items-center gap-2 mb-8">
          <Zap className="w-5 h-5 text-primary" />
          <span className="text-sm font-semibold text-gray-900">ExceptionOS Story Demo</span>
          <span className="text-xs text-gray-500">Step {step + 1} of {steps.length}</span>
        </div>

        <div className="flex gap-1 mb-8">
          {steps.map((_, i) => (
            <div key={i} className={`h-1 flex-1 rounded-full transition-all ${i <= step ? 'bg-primary' : 'bg-gray-100'}`} />
          ))}
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-8 mb-6 fade-in" key={step}>
          <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mb-4">
            {step === steps.length - 1 ? <CheckCircle className="w-7 h-7 text-green-600" /> : <span className="text-2xl font-bold text-primary">{step + 1}</span>}
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-3">{steps[step].title}</h2>
          <p className="text-gray-600 text-lg leading-relaxed">{steps[step].desc}</p>
        </div>

        <div className="flex gap-3 justify-between">
          <button onClick={() => setStep(Math.max(0, step - 1))} disabled={step === 0}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gray-100 hover:bg-gray-100 text-gray-900 font-medium transition-colors border border-gray-200 disabled:opacity-30">
            <ArrowLeft className="w-4 h-4" /> Previous
          </button>
          {step < steps.length - 1 ? (
            <button onClick={() => setStep(step + 1)} className="flex items-center gap-2 px-6 py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold transition-colors">
              Next <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button onClick={() => navigate('/signup')} className="flex items-center gap-2 px-6 py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold transition-colors">
              Get started free <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
