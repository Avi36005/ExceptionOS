import { useState } from 'react'
import { Mic, MicOff, Volume2, Brain } from 'lucide-react'

export default function VoiceAssistant() {
  const [listening, setListening] = useState(false)
  const [transcript, setTranscript] = useState('')

  const toggleListen = () => {
    setListening(l => {
      if (!l) {
        setTimeout(() => {
          setTranscript('Show me the status of exception EXC-1048')
        }, 1500)
      }
      return !l
    })
  }

  return (
    <div className="fade-in max-w-2xl mx-auto">
      <div className="text-center mb-10">
        <div className="flex items-center justify-center gap-3 mb-2">
          <Brain className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold text-gray-900">Voice Assistant</h1>
        </div>
        <p className="text-gray-500 text-sm">Query ExceptionOS hands-free. Ask about exceptions, policies, and decisions.</p>
      </div>

      <div className="flex flex-col items-center gap-8">
        {/* Voice button */}
        <div className="relative">
          {listening && (
            <>
              <div className="absolute inset-0 rounded-full bg-primary/20 animate-ping scale-150" />
              <div className="absolute inset-0 rounded-full bg-primary/10 animate-ping scale-125" style={{ animationDelay: '0.3s' }} />
            </>
          )}
          <button
            onClick={toggleListen}
            className={`relative w-32 h-32 rounded-full flex items-center justify-center transition-all shadow-2xl ${
              listening
                ? 'bg-primary hover:bg-primary-dark shadow-primary/30'
                : 'bg-gray-100 hover:bg-gray-100 border border-gray-300'
            }`}
          >
            {listening ? <MicOff className="w-12 h-12 text-white" /> : <Mic className="w-12 h-12 text-gray-900" />}
          </button>
        </div>

        <div className="text-center">
          <p className="text-sm font-medium text-gray-900 mb-1">{listening ? 'Listening...' : 'Tap to speak'}</p>
          <p className="text-xs text-gray-500">{listening ? 'Speak your query clearly' : 'Ask about any exception, policy, or precedent'}</p>
        </div>

        {/* Transcript */}
        {transcript && (
          <div className="w-full bg-white rounded-xl border border-gray-200 p-4 fade-in">
            <div className="text-xs text-gray-500 mb-2">You said:</div>
            <p className="text-sm text-gray-900 font-medium mb-4">"{transcript}"</p>
            <div className="bg-primary/5 border border-primary/20 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Brain className="w-4 h-4 text-primary" />
                <span className="text-xs font-semibold text-primary">Response</span>
              </div>
              <p className="text-sm text-gray-600">Exception EXC-1048 is currently <strong className="text-gray-900">Under Review</strong>. It was submitted by Alex Turner on December 18, 2024 for an emergency software license. The exception is assigned to Sarah Chen for approval. Deadline is December 20, 2024. Would you like me to open it?</p>
              <div className="flex gap-2 mt-3">
                <button className="px-3 py-1.5 rounded-lg bg-primary/10 hover:bg-primary/20 text-primary text-xs font-medium transition-colors">Open EXC-1048</button>
                <button className="px-3 py-1.5 rounded-lg bg-gray-50 hover:bg-gray-100 text-gray-600 text-xs font-medium transition-colors">Dismiss</button>
              </div>
            </div>
          </div>
        )}

        {/* Sample commands */}
        {!transcript && (
          <div className="w-full">
            <p className="text-xs text-gray-500 text-center mb-3">Try saying:</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {[
                '"Show me all pending approvals"',
                '"What is the status of EXC-1048?"',
                '"Create a new exception for IT software"',
                '"Find precedents for vendor exceptions"',
                '"How many exceptions were approved this month?"',
                '"Escalate EXC-1045 to Sarah Chen"',
              ].map(cmd => (
                <div key={cmd} className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg border border-gray-100">
                  <Volume2 className="w-3.5 h-3.5 text-gray-600 shrink-0" />
                  <span className="text-xs text-gray-500">{cmd}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
