import { getAccessToken } from './supabase'

const API = import.meta.env.VITE_EXCEPTIONOS_API_URL || ''

let currentAudio: HTMLAudioElement | null = null
let currentUrl: string | null = null

export interface AssistantReply {
  answer: string
  sources: { text: string }[]
  provider?: string
}

/** Ask the ExceptionOS assistant (real Groq LLM + Hindsight recall).
 *  opts.bankId  → query a specific org's Hindsight bank (org-aware)
 *  opts.context → current page/case context so answers are page-aware  */
export async function askAssistant(
  message: string,
  opts: { bankId?: string; context?: string } = {},
): Promise<AssistantReply> {
  const token = await getAccessToken()
  const res = await fetch(`${API}/api/v1/assistant/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ message, bank_id: opts.bankId, context: opts.context }),
  })
  if (!res.ok) {
    throw new Error(res.status === 401 ? 'Please sign in to chat' : `Assistant failed (${res.status})`)
  }
  const json = await res.json()
  const data = json.data || json
  return { answer: data.answer || '…', sources: data.sources || [], provider: data.provider }
}

/** Stop any in-flight ElevenLabs playback and free its object URL. */
export function stopSpeech() {
  if (currentAudio) {
    currentAudio.pause()
    currentAudio.currentTime = 0
    currentAudio = null
  }
  if (currentUrl) {
    URL.revokeObjectURL(currentUrl)
    currentUrl = null
  }
}

/**
 * Speak `text` using the REAL ElevenLabs voice via the backend
 * POST /api/v1/voice/synthesize (streams audio/mpeg). Resolves when playback
 * starts; `onended` fires when it finishes. Throws on any failure so callers
 * can surface an error — we never silently fall back to browser TTS.
 */
export async function speakWithElevenLabs(
  text: string,
  opts: { onended?: () => void } = {},
): Promise<HTMLAudioElement> {
  stopSpeech()
  const token = await getAccessToken()
  const res = await fetch(`${API}/api/v1/voice/synthesize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ text: text.slice(0, 2500) }),
  })
  if (!res.ok) {
    throw new Error(
      res.status === 503
        ? 'ElevenLabs is not configured on the server'
        : res.status === 401
          ? 'Please sign in to use voice'
          : `Voice failed (${res.status})`,
    )
  }
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  currentUrl = url
  const audio = new Audio(url)
  currentAudio = audio
  audio.onended = () => {
    if (opts.onended) opts.onended()
    stopSpeech()
  }
  await audio.play()
  return audio
}
