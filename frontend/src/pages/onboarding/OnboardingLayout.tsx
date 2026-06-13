import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { Zap, Check } from 'lucide-react'

const steps = [
  { path: 'company', label: 'Company Setup' },
  { path: 'policies', label: 'Policies' },
  { path: 'team', label: 'Team' },
  { path: 'hindsight', label: 'Hindsight™' },
]

export default function OnboardingLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const currentStep = steps.findIndex(s => location.pathname.includes(s.path))

  return (
    <div className="min-h-screen bg-dark">
      {/* Header */}
      <div className="border-b border-white/10 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <Zap className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-white">ExceptionOS</span>
        </div>
        <button onClick={() => navigate('/select-organization')} className="text-sm text-gray-400 hover:text-white transition-colors">
          Skip setup
        </button>
      </div>

      {/* Progress */}
      <div className="max-w-3xl mx-auto px-6 pt-10 pb-4">
        <div className="flex items-center justify-between mb-8">
          {steps.map((step, i) => (
            <div key={step.path} className="flex items-center">
              <div className="flex flex-col items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold transition-all ${
                  i < currentStep ? 'bg-primary text-white' :
                  i === currentStep ? 'bg-primary text-white ring-2 ring-primary/30 ring-offset-2 ring-offset-dark' :
                  'bg-white/10 text-gray-500'
                }`}>
                  {i < currentStep ? <Check className="w-4 h-4" /> : i + 1}
                </div>
                <span className={`text-xs mt-1 font-medium ${i <= currentStep ? 'text-white' : 'text-gray-600'}`}>
                  {step.label}
                </span>
              </div>
              {i < steps.length - 1 && (
                <div className={`h-0.5 flex-1 mx-3 mb-5 ${i < currentStep ? 'bg-primary' : 'bg-white/10'}`} style={{ width: 80 }} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="max-w-2xl mx-auto px-6 pb-16">
        <Outlet />
      </div>
    </div>
  )
}
