import { useState, useRef, useEffect } from 'react'
import { Mic, MicOff, Volume2, Square, Brain, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { speakWithElevenLabs, stopSpeech } from '../../../lib/voice'

const RESPONSE =
  'Exception EXC-1048 is currently Under Review. It was submitted by Alex Turner for an emergency software license and is assigned to Sarah Chen for approval. The deadline is in two days. Based on Hindsight, three similar license exceptions were approved this quarter. Would you like me to open it?'

export default function VoiceAssistant() {
  const [listening, setListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [speaking, setSpeaking] = useState(false)
  const [loading, setLoading] = useState(false)
  const recognitionRef = useRef<any>(null)

  // Real browser speech-to-text (Web Speech API) for the query.
  useEffect(() => {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SR) return
    const rec = new SR()
    rec.continuous = false
    rec.interimResults = false
    rec.lang = 'en-US'
    rec.onresult = (e: any) => setTranscript(e.results[0][0].transcript)
    rec.onend = () => setListening(false)
    rec.onerror = () => setListening(false)
    recognitionRef.current = rec
    return () => { try { rec.stop() } catch { /* noop */ } }
  }, [])

  const toggleListen = () => {
    const rec = recognitionRef.current
    if (!rec) {
      toast.error('Speech recognition not supported in this browser — try Chrome')
      return
    }
    if (listening) { rec.stop(); setListening(false) }
    else { setTranscript(''); rec.start(); setListening(true) }
  }

  // Real ElevenLabs playback of the assistant response.
  const speakResponse = async () => {
    if (speaking || loading) { stopSpeech(); setSpeaking(false); setLoading(false); return }
    setLoading(true)
    try {
      await speakWithElevenLabs(RESPONSE, { onended: () => setSpeaking(false) })
      setSpeaking(true)
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : 'Voice failed')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => () => stopSpeech(), [])

  return (
    <div className="fade-in max-w-2xl mx-auto">
      <div className="text-center mb-10">
        <div className="flex items-center justify-center gap-3 mb-2">
          <Brain className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold text-gray-900">Voice Assistant</h1>
        </div>
        <p className="text-gray-500 text-sm">Query ExceptionOS hands-free. Powered by real ElevenLabs voice.</p>
      </div>

      <div className="flex flex-col items-center gap-8">
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
              listening ? 'bg-primary hover:bg-primary-dark shadow-primary/30' : 'bg-gray-100 hover:bg-gray-200 border border-gray-300'
            }`}
          >
            {listening ? <MicOff className="w-12 h-12 text-white" /> : <Mic className="w-12 h-12 text-gray-900" />}
          </button>
        </div>

        <div className="text-center">
          <p className="text-sm font-medium text-gray-900 mb-1">{listening ? 'Listening...' : 'Tap to speak'}</p>
          <p className="text-xs text-gray-500">{listening ? 'Speak your query clearly' : 'Ask about any exception, policy, or precedent'}</p>
        </div>

        {transcript && (
          <div className="w-full bg-white rounded-xl border border-gray-200 p-4 fade-in shadow-card">
            <div className="text-xs text-gray-500 mb-2">You said:</div>
            <p className="text-sm text-gray-900 font-medium mb-4">"{transcript}"</p>
            <div className="bg-primary/5 border border-primary/20 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Brain className="w-4 h-4 text-primary" />
                  <span className="text-xs font-semibold text-primary">Response</span>
                </div>
                <button
                  onClick={speakResponse}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-primary/10 hover:bg-primary/20 text-primary text-xs font-medium transition-colors"
                >
                  {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : speaking ? <Square className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
                  {loading ? 'Preparing' : speaking ? 'Stop' : 'Speak'}
                </button>
              </div>
              <p className="text-sm text-gray-600">{RESPONSE}</p>
            </div>
          </div>
        )}

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
