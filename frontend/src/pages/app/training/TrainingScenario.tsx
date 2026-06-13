import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, CheckCircle, XCircle, ArrowRight } from 'lucide-react'

const scenario = {
  title: 'When to Approve an Emergency Exception',
  steps: [
    {
      question: 'A team member submits an emergency exception to bypass the 30-day software procurement process, citing a client presentation in 3 days. The software costs $2,500/year. What is your FIRST action?',
      options: [
        { text: 'Approve immediately since it\'s under $5,000', correct: false, feedback: 'Financial amount alone doesn\'t justify bypassing review. You need to assess the business case.' },
        { text: 'Review the business justification and ask for quantified impact', correct: true, feedback: 'Correct! First assess the business justification. Ask for quantified impact (revenue at risk, customer value, etc.).' },
        { text: 'Reject it — the 30-day process exists for a reason', correct: false, feedback: 'Rejecting without review isn\'t the right approach. Emergency exceptions exist in policy for genuine reasons.' },
        { text: 'Escalate to your manager', correct: false, feedback: 'Escalation may be premature. You should first assess whether you have the authority and information to decide.' },
      ],
    },
    {
      question: 'The requester provides evidence of a $150,000 deal that requires this tool for the presentation. The vendor is already on your approved list. What do you do next?',
      options: [
        { text: 'Approve with a 90-day time limit and note the conditions', correct: true, feedback: 'Excellent! Business impact is quantified, vendor is approved, and a time-limited approval with conditions is the correct framework.' },
        { text: 'Approve unconditionally', correct: false, feedback: 'Unconditional approval sets a precedent without controls. Always attach appropriate conditions.' },
        { text: 'Request CISO sign-off before deciding', correct: false, feedback: 'If the vendor is already approved, CISO review may not be needed. This would delay unnecessarily.' },
        { text: 'Ask for more documentation', correct: false, feedback: 'You already have sufficient information: quantified impact, approved vendor, clear timeline. More documentation would delay unnecessarily.' },
      ],
    },
  ],
}

export default function TrainingScenario() {
  const { scenarioId } = useParams()
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [selected, setSelected] = useState<number | null>(null)
  const [showFeedback, setShowFeedback] = useState(false)
  const [score, setScore] = useState(0)
  const [done, setDone] = useState(false)

  const current = scenario.steps[step]

  const handleSelect = (i: number) => {
    if (showFeedback) return
    setSelected(i)
    setShowFeedback(true)
    if (current.options[i].correct) setScore(s => s + 1)
  }

  const handleNext = () => {
    if (step < scenario.steps.length - 1) {
      setStep(s => s + 1)
      setSelected(null)
      setShowFeedback(false)
    } else {
      setDone(true)
    }
  }

  if (done) {
    return (
      <div className="fade-in max-w-lg mx-auto text-center py-12">
        <div className="w-20 h-20 rounded-3xl bg-primary/10 flex items-center justify-center mx-auto mb-6">
          <CheckCircle className="w-10 h-10 text-primary" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Scenario Complete!</h2>
        <p className="text-gray-400 mb-2">You scored <span className="text-white font-semibold">{score}/{scenario.steps.length}</span></p>
        <p className="text-sm text-gray-500 mb-8">{score === scenario.steps.length ? 'Perfect score! Excellent decision-making.' : 'Good effort. Review the feedback for areas to improve.'}</p>
        <div className="flex gap-3 justify-center">
          <button onClick={() => navigate('/app/training')} className="px-6 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 text-white font-medium text-sm border border-white/10 transition-colors">
            Back to Library
          </button>
          <button onClick={() => { setStep(0); setSelected(null); setShowFeedback(false); setScore(0); setDone(false) }} className="px-6 py-2.5 rounded-xl bg-primary hover:bg-primary-dark text-white font-medium text-sm transition-colors">
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="fade-in max-w-2xl">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate('/app/training')} className="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div className="flex-1">
          <h1 className="text-lg font-bold text-white">{scenario.title}</h1>
          <p className="text-sm text-gray-400">Step {step + 1} of {scenario.steps.length}</p>
        </div>
      </div>

      <div className="flex gap-1 mb-6">
        {scenario.steps.map((_, i) => (
          <div key={i} className={`h-1 flex-1 rounded-full ${i < step ? 'bg-primary' : i === step ? 'bg-primary/60' : 'bg-white/10'}`} />
        ))}
      </div>

      <div className="bg-dark2 rounded-2xl border border-white/10 p-6 mb-4">
        <p className="text-sm font-medium text-white leading-relaxed">{current.question}</p>
      </div>

      <div className="space-y-3 mb-6">
        {current.options.map((opt, i) => (
          <button key={i} onClick={() => handleSelect(i)}
            className={`w-full text-left p-4 rounded-xl border text-sm transition-all ${
              !showFeedback ? 'bg-white/5 border-white/10 hover:border-primary/40 text-gray-300' :
              i === selected && opt.correct ? 'bg-green-500/10 border-green-500/30 text-green-300' :
              i === selected && !opt.correct ? 'bg-red-500/10 border-red-500/30 text-red-300' :
              opt.correct ? 'bg-green-500/5 border-green-500/20 text-gray-400' :
              'bg-white/3 border-white/5 text-gray-500'
            }`}>
            <div className="flex items-start gap-3">
              <span className="w-5 h-5 rounded-full border border-current flex items-center justify-center text-xs shrink-0 mt-0.5">
                {showFeedback && opt.correct ? '✓' : showFeedback && i === selected && !opt.correct ? '✗' : String.fromCharCode(65 + i)}
              </span>
              <span>{opt.text}</span>
            </div>
          </button>
        ))}
      </div>

      {showFeedback && selected !== null && (
        <div className={`p-4 rounded-xl border mb-4 fade-in ${current.options[selected].correct ? 'bg-green-500/10 border-green-500/20' : 'bg-red-500/10 border-red-500/20'}`}>
          <div className="flex items-center gap-2 mb-1">
            {current.options[selected].correct ? <CheckCircle className="w-4 h-4 text-green-400" /> : <XCircle className="w-4 h-4 text-red-400" />}
            <span className={`text-sm font-semibold ${current.options[selected].correct ? 'text-green-400' : 'text-red-400'}`}>
              {current.options[selected].correct ? 'Correct!' : 'Not quite right'}
            </span>
          </div>
          <p className="text-sm text-gray-300">{current.options[selected].feedback}</p>
        </div>
      )}

      {showFeedback && (
        <button onClick={handleNext} className="flex items-center justify-center gap-2 w-full py-3 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold transition-colors fade-in">
          {step < scenario.steps.length - 1 ? 'Next Question' : 'See Results'}
          <ArrowRight className="w-4 h-4" />
        </button>
      )}
    </div>
  )
}
