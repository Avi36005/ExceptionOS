import type { JsonObject } from './common'

export interface VoiceSynthesizeRequest {
  text: string
  voice_id?: string
  model_id?: string
}

export interface VoiceVoice {
  voice_id: string
  name: string
  [key: string]: unknown
}

/**
 * Voice session — extensible placeholder for the not-yet-finalized
 * /app/voice/:sessionId and /app/voice/history endpoints. The frontend
 * spec calls for: connection state, live transcript, agent transcript,
 * tool calls, extracted case fields, confirmation prompts.
 */
export interface VoiceSession {
  id: string
  organization_id?: string
  status?: 'active' | 'completed' | 'failed'
  transcript?: VoiceTranscriptEntry[]
  extracted_fields?: JsonObject
  linked_case_id?: string | null
  created_at?: string
  updated_at?: string
  [key: string]: unknown
}

export interface VoiceTranscriptEntry {
  role: 'user' | 'agent' | 'system'
  text: string
  ts?: string
  [key: string]: unknown
}

export interface VoiceSessionRequest {
  voice_id?: string
  [key: string]: unknown
}
