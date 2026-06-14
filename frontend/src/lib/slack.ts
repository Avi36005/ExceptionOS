import { getAccessToken } from './supabase'

const API = import.meta.env.VITE_EXCEPTIONOS_API_URL || ''

async function post(path: string, body?: unknown) {
  const token = await getAccessToken()
  const res = await fetch(`${API}/api/v1/integrations/slack/${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body || {}),
  })
  if (!res.ok) throw new Error(res.status === 401 ? 'Please sign in' : `Slack failed (${res.status})`)
  const json = await res.json()
  return (json.data || json) as { sent?: boolean; message?: string }
}

/** Send a Slack test message. */
export const slackTest = () => post('test')

/** Send a structured Slack notification (event/case fields or {text}). */
export const slackNotify = (payload: Record<string, unknown>) => post('notify', payload)
