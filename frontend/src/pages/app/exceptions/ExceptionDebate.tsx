import { ThumbsUp, ThumbsDown, Brain, RefreshCw } from 'lucide-react'
import { useState } from 'react'

const initialDebate = {
  proArguments: [
    { text: 'Business impact is quantifiable and significant ($120K revenue at risk). Precedent PREC-0234 shows this type of emergency was approved under similar circumstances.', strength: 'strong' },
    { text: 'The 5-day vs 30-day timeline conflict is a genuine structural constraint, not a planning failure. The accelerated launch was approved by executive leadership after the procurement process began.', strength: 'strong' },
    { text: 'Vendor (Figma) is an approved and vetted software provider already used by 3 other teams. Security review can be expedited given existing approval status.', strength: 'medium' },
    { text: 'Emergency provision in Budget Authorization Policy (POL-FIN-008 §3.1) explicitly permits this type of expedited approval with department head authorization.', strength: 'medium' },
  ],
  conArguments: [
    { text: 'Pattern risk: This is the 3rd IT software emergency exception in Q4. Approving repeatedly without addressing root cause signals procurement process dysfunction.', strength: 'strong' },
    { text: 'Amount ($4,500/yr) is within normal budget authority. Labeling this "emergency" may set precedent that circumvents standard controls for routine purchases.', strength: 'medium' },
    { text: 'CISO sign-off on security is required per POL-IT-001 §2.4 even for emergency exceptions. This step has not been completed in the request.', strength: 'strong' },
  ],
}

const strengthColors: Record<string, string> = {
  strong: 'border-l-primary',
  medium: 'border-l-yellow-500/50',
  weak: 'border-l-gray-600',
}

export default function ExceptionDebate() {
  const [regenerating, setRegenerating] = useState(false)

  const handleRegenerate = async () => {
    setRegenerating(true)
    await new Promise(r => setTimeout(r, 2000))
    setRegenerating(false)
  }

  return (
    <div className="fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-primary" />
          <span className="text-sm font-semibold text-white">AI Adversarial Debate</span>
          <span className="text-xs text-gray-500">— Both sides of the decision analyzed</span>
        </div>
        <button onClick={handleRegenerate} disabled={regenerating} className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 text-xs font-medium border border-white/10 transition-colors disabled:opacity-50">
          <RefreshCw className={`w-3.5 h-3.5 ${regenerating ? 'animate-spin' : ''}`} />
          Regenerate
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pro */}
        <div className="bg-dark2 rounded-xl border border-white/10 p-5">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center">
              <ThumbsUp className="w-4 h-4 text-green-400" />
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Arguments For Approval</div>
              <div className="text-xs text-gray-500">{initialDebate.proArguments.length} points identified</div>
            </div>
          </div>
          <div className="space-y-3">
            {initialDebate.proArguments.map((arg, i) => (
              <div key={i} className={`border-l-2 pl-3 ${strengthColors[arg.strength]}`}>
                <p className="text-xs text-gray-300 leading-relaxed">{arg.text}</p>
                <span className={`text-xs font-medium mt-1 inline-block capitalize ${arg.strength === 'strong' ? 'text-primary' : 'text-yellow-400'}`}>{arg.strength} argument</span>
              </div>
            ))}
          </div>
        </div>

        {/* Con */}
        <div className="bg-dark2 rounded-xl border border-white/10 p-5">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center">
              <ThumbsDown className="w-4 h-4 text-red-400" />
            </div>
            <div>
              <div className="text-sm font-semibold text-white">Arguments Against Approval</div>
              <div className="text-xs text-gray-500">{initialDebate.conArguments.length} points identified</div>
            </div>
          </div>
          <div className="space-y-3">
            {initialDebate.conArguments.map((arg, i) => (
              <div key={i} className={`border-l-2 pl-3 ${strengthColors[arg.strength]}`}>
                <p className="text-xs text-gray-300 leading-relaxed">{arg.text}</p>
                <span className={`text-xs font-medium mt-1 inline-block capitalize ${arg.strength === 'strong' ? 'text-red-400' : 'text-yellow-400'}`}>{arg.strength} argument</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-primary/5 border border-primary/20 rounded-xl p-5">
        <div className="text-xs font-semibold text-primary mb-2 uppercase tracking-wide">Debate Summary</div>
        <p className="text-sm text-gray-300 leading-relaxed">
          The case for approval is strong on business impact and precedent grounds, but two procedural gaps exist: CISO sign-off and the systemic pattern of IT emergency exceptions in Q4.
          Approving with conditions (CISO review within 24h, 60-day license cap, mandatory procurement process review) is the recommended path.
        </p>
      </div>
    </div>
  )
}
