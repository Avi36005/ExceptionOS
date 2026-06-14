import { useState, useRef, useEffect, useCallback } from 'react'
import { Mic, Send, X, Volume2, Square, Loader2, Sparkles, MessageSquare } from 'lucide-react'
import toast from 'react-hot-toast'
import { speakWithElevenLabs, stopSpeech, askAssistant } from '../../lib/voice'

interface Msg { role: 'user' | 'assistant'; text: string }

/**
 * Global floating assistant orb — REAL chat + REAL voice, on every page.
 * Chat answers come from the live Groq LLM grounded in Hindsight recall
 * (POST /api/v1/assistant/chat); spoken replies use the real ElevenLabs voice
 * (POST /api/v1/voice/synthesize). Also reads the current page aloud.
 */
export default function VoiceOrb() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Msg[]>([
    { role: 'assistant', text: 'Hi! Ask me about exceptions, policies, or precedents — I can speak my answers too.' },
  ])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [speakingIdx, setSpeakingIdx] = useState<number | null>(null)
  const [listening, setListening] = useState(false)
  const recRef = useRef<any>(null)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, open])

  // Real browser speech-to-text for the chat input.
  useEffect(() => {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SR) return
    const rec = new SR()
    rec.continuous = false; rec.interimResults = false; rec.lang = 'en-US'
    rec.onresult = (e: any) => setInput(e.results[0][0].transcript)
    rec.onend = () => setListening(false)
    rec.onerror = () => setListening(false)
    recRef.current = rec
    return () => { try { rec.stop() } catch { /* noop */ } }
  }, [])

  const speak = useCallback(async (text: string, idx: number) => {
    if (speakingIdx === idx) { stopSpeech(); setSpeakingIdx(null); return }
    try {
      setSpeakingIdx(idx)
      await speakWithElevenLabs(text, { onended: () => setSpeakingIdx(null) })
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : 'Voice failed')
      setSpeakingIdx(null)
    }
  }, [speakingIdx])

  const send = useCallback(async (text: string) => {
    const q = text.trim()
    if (!q || sending) return
    setInput('')
    setMessages(m => [...m, { role: 'user', text: q }])
    setSending(true)
    try {
      const reply = await askAssistant(q)
      setMessages(m => {
        const next: Msg[] = [...m, { role: 'assistant', text: reply.answer }]
        // Auto-speak the answer with real ElevenLabs.
        speak(reply.answer, next.length - 1)
        return next
      })
    } catch (err: unknown) {
      setMessages(m => [...m, { role: 'assistant', text: err instanceof Error ? err.message : 'Something went wrong.' }])
    } finally {
      setSending(false)
    }
  }, [sending, speak])

  const toggleMic = () => {
    const rec = recRef.current
    if (!rec) { toast.error('Speech input needs Chrome'); return }
    if (listening) { rec.stop(); setListening(false) }
    else { rec.start(); setListening(true) }
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
      {open && (
        <div className="w-[360px] max-w-[calc(100vw-3rem)] h-[480px] bg-white rounded-2xl border border-gray-200 shadow-card-hover flex flex-col overflow-hidden fade-in">
          {/* Header */}
          <div className="flex items-center justify-between px-4 h-14 bg-gradient-to-r from-primary to-[#7C5CFF] text-white shrink-0">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              <span className="text-sm font-semibold">ExceptionOS Assistant</span>
            </div>
            <button onClick={() => setOpen(false)} aria-label="Close" className="p-1 rounded-lg hover:bg-white/15">
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 bg-light">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm ${
                  m.role === 'user' ? 'bg-primary text-white rounded-br-sm' : 'bg-white border border-gray-200 text-gray-800 rounded-bl-sm'
                }`}>
                  <p>{m.text}</p>
                  {m.role === 'assistant' && (
                    <button
                      onClick={() => speak(m.text, i)}
                      className="mt-1.5 flex items-center gap-1 text-[11px] font-medium text-primary hover:underline"
                    >
                      {speakingIdx === i ? <Square className="w-3 h-3" /> : <Volume2 className="w-3 h-3" />}
                      {speakingIdx === i ? 'Stop' : 'Speak'}
                    </button>
                  )}
                </div>
              </div>
            ))}
            {sending && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-3 py-2">
                  <Loader2 className="w-4 h-4 animate-spin text-primary" />
                </div>
              </div>
            )}
            <div ref={endRef} />
          </div>

          {/* Input */}
          <div className="p-3 border-t border-gray-200 bg-white shrink-0">
            <div className="flex items-center gap-2">
              <button
                onClick={toggleMic}
                aria-label="Speak"
                className={`p-2 rounded-lg shrink-0 transition-colors ${listening ? 'bg-primary text-white animate-pulse' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
              >
                <Mic className="w-4 h-4" />
              </button>
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') send(input) }}
                placeholder={listening ? 'Listening…' : 'Ask anything…'}
                className="flex-1 min-w-0 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-primary/60 focus:ring-2 focus:ring-primary/15"
              />
              <button
                onClick={() => send(input)}
                disabled={sending || !input.trim()}
                aria-label="Send"
                className="p-2 rounded-lg bg-primary text-white shrink-0 disabled:opacity-50 hover:bg-primary-dark transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Orb */}
      <button
        onClick={() => setOpen(o => !o)}
        aria-label="Open assistant"
        className="relative w-14 h-14 rounded-full flex items-center justify-center text-white shadow-[0_10px_30px_rgba(91,91,240,.5)] bg-gradient-to-br from-primary to-[#7C5CFF] hover:scale-105 active:scale-95 transition-transform"
      >
        {speakingIdx !== null && (
          <>
            <span className="absolute inset-0 rounded-full bg-primary/30 animate-ping" />
            <span className="absolute inset-0 rounded-full bg-primary/20 animate-ping" style={{ animationDelay: '.4s' }} />
          </>
        )}
        {open ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
      </button>
    </div>
  )
}
