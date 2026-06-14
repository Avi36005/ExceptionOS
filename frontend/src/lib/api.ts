/**
 * Typed API client for the ExceptionOS backend (`/api/v1/...`).
 *
 * Conventions:
 * - Base URL from `VITE_EXCEPTIONOS_API_URL` (default `http://localhost:8000`).
 * - Every authenticated request attaches `Authorization: Bearer <supabase access token>`.
 * - Organisation scoping is via the `organization_id` query parameter (confirmed
 *   against `backend/app/dependencies.require_org_member` and route files such as
 *   `exceptions.py` / `organizations.py`, which declare `organization_id: UUID = Query(...)`).
 *   Resource methods that are org-scoped take `orgId` as their first argument.
 * - All responses are wrapped as `{ data, meta? }` (see `DataResponse<T>` in
 *   `lib/types/common.ts`); `request()` returns the parsed envelope so callers
 *   can access `meta` (pagination) when present. Use `.data` accessors below
 *   for resource methods that only need the payload.
 * - Non-2xx responses throw `ApiError` with normalized `status`/`body`.
 * - On 401, the Supabase session is cleared and the user is redirected to /login
 *   (mirrors the previous axios interceptor behaviour).
 */
import { getAccessToken, supabase } from './supabase'
import { ApiError } from './types/common'
import type {
  DataResponse,
  MessageResponse,
  ListParams,
  JsonObject,
} from './types/common'
import type {
  Organization,
  OrganizationCreate,
  OrganizationUpdate,
  OrganizationMembership,
  OrganizationMember,
  Profile,
  UserInvite,
} from './types/organizations'
import type {
  ExceptionCase,
  ExceptionCaseCreate,
  ExceptionCaseUpdate,
  ExceptionListParams,
  Recommendation,
  Decision,
  DecisionCreate,
  Outcome,
  OutcomeCreate,
  PrecedentLink,
  CaseMemoryResponse,
  AuditEvent,
  AnalyzeRequest,
  IntakeResult,
  AnswerQuestionRequest,
} from './types/exceptions'
import type {
  Policy,
  PolicyCreate,
  PolicyUpdate,
  PolicyListParams,
} from './types/policies'
import type {
  PrecedentSearchParams,
  PrecedentSearchResult,
  PrecedentLinkRow,
  PrecedentGraph,
  PrecedentAskRequest,
  PrecedentAskResponse,
  PrecedentContradiction,
} from './types/precedents'
import type {
  DashboardMetrics,
  PolicyDriftFinding,
  RepeatedExceptionPattern,
  InsightsGenericResponse,
} from './types/insights'
import type {
  TrainingScenario,
  TrainingScenarioRunResult,
  TrainingHistoryEntry,
} from './types/training'
import type {
  RetainRequest,
  RecallRequest,
  ReflectRequest,
  RecallResponse,
  ReflectResponse,
} from './types/memory'
import type {
  VoiceSynthesizeRequest,
  VoiceVoice,
  VoiceSession,
  VoiceSessionRequest,
} from './types/voice'
import type {
  AdminStats,
  AdminOrganizationList,
  SystemHealthStatus,
} from './types/admin'
import type { NotificationItem } from './types/notifications'
import type {
  DemoStatus,
  DemoResetResponse,
  ReplayTimeline,
  WhatChangedResponse,
  AnswerQuestionResponse,
} from './types/demo'

const API_URL = import.meta.env.VITE_EXCEPTIONOS_API_URL || 'http://localhost:8000'

// ---------------------------------------------------------------------------
// Core request helper
// ---------------------------------------------------------------------------

export interface RequestOptions extends Omit<RequestInit, 'body'> {
  /** Query parameters appended to the URL (undefined/null values are skipped). */
  query?: Record<string, unknown>
  /** JSON-serializable request body. */
  body?: unknown
  /** AbortSignal for request cancellation (e.g. on route change). */
  signal?: AbortSignal
}

function buildUrl(path: string, query?: Record<string, unknown>): string {
  const url = new URL(path.replace(/^\/+/, ''), `${API_URL.replace(/\/+$/, '')}/`)
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value === undefined || value === null) continue
      if (Array.isArray(value)) {
        for (const v of value) url.searchParams.append(key, String(v))
      } else {
        url.searchParams.set(key, String(value))
      }
    }
  }
  return url.toString()
}

/**
 * Low-level typed request. Returns the parsed JSON body (typically a
 * `DataResponse<T>` or `MessageResponse<T>` envelope — callers narrow via
 * the generic parameter).
 */
export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { query, body, headers, ...rest } = options

  const url = buildUrl(`/api/v1/${path.replace(/^\/+/, '')}`, query)

  const token = await getAccessToken()
  const finalHeaders: Record<string, string> = {
    Accept: 'application/json',
    ...(headers as Record<string, string> | undefined),
  }
  if (body !== undefined) {
    finalHeaders['Content-Type'] = 'application/json'
  }
  if (token) {
    finalHeaders.Authorization = `Bearer ${token}`
  }

  let response: Response
  try {
    response = await fetch(url, {
      ...rest,
      headers: finalHeaders,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch (err) {
    throw new ApiError(
      err instanceof Error ? err.message : 'Network request failed',
      0,
      null,
      url,
    )
  }

  if (response.status === 401) {
    await supabase.auth.signOut()
    if (typeof window !== 'undefined') {
      window.location.href = '/login'
    }
  }

  if (response.status === 204) {
    return undefined as T
  }

  const text = await response.text()
  const json = text ? safeJsonParse(text) : null

  if (!response.ok) {
    const message =
      (json && typeof json === 'object' && 'detail' in json
        ? String((json as Record<string, unknown>).detail)
        : null) ||
      (json && typeof json === 'object' && 'error' in json
        ? String((json as Record<string, unknown>).error)
        : null) ||
      `Request failed with status ${response.status}`
    throw new ApiError(message, response.status, json as never, url)
  }

  return json as T
}

function safeJsonParse(text: string): unknown {
  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}

// Convenience wrappers that unwrap `DataResponse<T>` -> T
async function getData<T>(path: string, options?: RequestOptions): Promise<T> {
  const res = await request<DataResponse<T>>(path, { ...options, method: 'GET' })
  return res.data
}

async function getDataWithMeta<T>(path: string, options?: RequestOptions): Promise<DataResponse<T>> {
  return request<DataResponse<T>>(path, { ...options, method: 'GET' })
}

async function postData<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
  const res = await request<DataResponse<T>>(path, { ...options, method: 'POST', body })
  return res.data
}

async function patchData<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
  const res = await request<DataResponse<T>>(path, { ...options, method: 'PATCH', body })
  return res.data
}

async function deleteData(path: string, options?: RequestOptions): Promise<void> {
  await request<void>(path, { ...options, method: 'DELETE' })
}

// ---------------------------------------------------------------------------
// Resource: Organizations
// ---------------------------------------------------------------------------

export const organizationsApi = {
  list: (params: ListParams = {}) =>
    getDataWithMeta<Organization[]>('organizations/', { query: params }),
  get: (organizationId: string) => getData<Organization>(`organizations/${organizationId}`),
  create: (payload: OrganizationCreate) => postData<Organization>('organizations/', payload),
  update: (organizationId: string, payload: OrganizationUpdate) =>
    patchData<Organization>(`organizations/${organizationId}`, payload),
  remove: (organizationId: string) => deleteData(`organizations/${organizationId}`),
}

// ---------------------------------------------------------------------------
// Resource: Users / membership
// ---------------------------------------------------------------------------

export const usersApi = {
  me: () => getData<Profile>('users/me'),
  myOrganizations: () => getData<OrganizationMembership[]>('users/me/organizations'),
  listMembers: (organizationId: string) =>
    getData<OrganizationMember[]>(`users/${organizationId}/members`),
  invite: (organizationId: string, payload: UserInvite) =>
    request<MessageResponse>(`users/${organizationId}/members/invite`, {
      method: 'POST',
      body: payload,
    }),
  removeMember: (organizationId: string, userId: string) =>
    deleteData(`users/${organizationId}/members/${userId}`),
}

// ---------------------------------------------------------------------------
// Resource: Exceptions (cases)
// ---------------------------------------------------------------------------

export const exceptionsApi = {
  list: (orgId: string, params: ExceptionListParams = {}) =>
    getDataWithMeta<ExceptionCase[]>('exceptions/', {
      query: { organization_id: orgId, ...params },
    }),
  get: (orgId: string, caseId: string) =>
    getData<ExceptionCase>(`exceptions/${caseId}`, { query: { organization_id: orgId } }),
  create: (orgId: string, payload: ExceptionCaseCreate) =>
    postData<ExceptionCase>('exceptions/', payload, { query: { organization_id: orgId } }),
  update: (orgId: string, caseId: string, payload: ExceptionCaseUpdate) =>
    patchData<ExceptionCase>(`exceptions/${caseId}`, payload, {
      query: { organization_id: orgId },
    }),

  /** Run the intake agent to extract structured facts from the case. */
  runIntake: (orgId: string, caseId: string) =>
    postData<IntakeResult>(`exceptions/${caseId}/intake`, undefined, {
      query: { organization_id: orgId },
    }),

  /** Trigger the multi-agent debate in the background (non-streaming). Use
   *  `useDebateStream` for live progress via SSE. */
  triggerAnalysis: (orgId: string, caseId: string, payload: AnalyzeRequest = {}) =>
    request<MessageResponse>(`exceptions/${caseId}/analyze`, {
      method: 'POST',
      body: payload,
      query: { organization_id: orgId },
    }),

  getRecommendation: (orgId: string, caseId: string) =>
    getData<Recommendation>(`exceptions/${caseId}/recommendation`, {
      query: { organization_id: orgId },
    }),

  recordDecision: (orgId: string, caseId: string, payload: DecisionCreate) =>
    postData<Decision>(`exceptions/${caseId}/decision`, payload, {
      query: { organization_id: orgId },
    }),

  recordOutcome: (orgId: string, caseId: string, payload: OutcomeCreate) =>
    postData<Outcome>(`exceptions/${caseId}/outcome`, payload, {
      query: { organization_id: orgId },
    }),

  getPrecedents: (orgId: string, caseId: string) =>
    getData<PrecedentLink[]>(`exceptions/${caseId}/precedents`, {
      query: { organization_id: orgId },
    }),

  getMemory: (orgId: string, caseId: string) =>
    getData<CaseMemoryResponse>(`exceptions/${caseId}/memory`, {
      query: { organization_id: orgId },
    }),

  getAuditTrail: (orgId: string, caseId: string) =>
    getData<AuditEvent[]>(`exceptions/${caseId}/audit`, { query: { organization_id: orgId } }),

  /**
   * Decision replay timeline. Endpoint path is a best guess
   * (`/exceptions/{caseId}/replay`) pending the backend agent's final route —
   * adjust here if it lands elsewhere; callers only depend on this function.
   */
  getReplay: (orgId: string, caseId: string) =>
    getData<ReplayTimeline>(`exceptions/${caseId}/replay`, { query: { organization_id: orgId } }),

  /**
   * Recommendation version diff ("what changed"). Endpoint path is a best
   * guess (`/exceptions/{caseId}/what-changed`) pending the backend agent's
   * final route.
   */
  getWhatChanged: (orgId: string, caseId: string) =>
    getData<WhatChangedResponse>(`exceptions/${caseId}/what-changed`, {
      query: { organization_id: orgId },
    }),

  /**
   * Answer a Missing-Information-Agent question inline. Endpoint path is a
   * best guess (`/exceptions/{caseId}/answer-question`) pending the backend
   * agent's final route.
   */
  answerQuestion: (orgId: string, caseId: string, payload: AnswerQuestionRequest) =>
    postData<AnswerQuestionResponse>(`exceptions/${caseId}/answer-question`, payload, {
      query: { organization_id: orgId },
    }),

  /** SSE debate stream URL (consumed by `useDebateStream`, not `fetch`-ed directly here). */
  debateStreamUrl: (orgId: string, caseId: string, demoMode = false) =>
    buildUrl(`/api/v1/exceptions/${caseId}/debate`, {
      organization_id: orgId,
      demo_mode: demoMode || undefined,
    }),
}

// ---------------------------------------------------------------------------
// Resource: Debate (agent runs)
// ---------------------------------------------------------------------------

export const debateApi = {
  listAgentRuns: (caseId: string) => getData<JsonObject[]>(`debate/${caseId}/agent-runs`),
  /** Alternate SSE debate stream URL exposed under /debate/{case_id}/stream. */
  streamUrl: (orgId: string, caseId: string, demoMode = false) =>
    buildUrl(`/api/v1/debate/${caseId}/stream`, {
      organization_id: orgId,
      demo_mode: demoMode || undefined,
    }),
}

// ---------------------------------------------------------------------------
// Resource: Decisions / Outcomes / Recommendations (top-level list views)
// ---------------------------------------------------------------------------

export const decisionsApi = {
  list: (orgId: string, caseId?: string) =>
    getData<Decision[]>('decisions/', { query: { organization_id: orgId, case_id: caseId } }),
  get: (decisionId: string) => getData<Decision>(`decisions/${decisionId}`),
}

export const outcomesApi = {
  list: (orgId: string, caseId?: string) =>
    getData<Outcome[]>('outcomes/', { query: { organization_id: orgId, case_id: caseId } }),
  get: (outcomeId: string) => getData<Outcome>(`outcomes/${outcomeId}`),
}

export const recommendationsApi = {
  list: (orgId: string, caseId?: string) =>
    getData<Recommendation[]>('recommendations/', {
      query: { organization_id: orgId, case_id: caseId },
    }),
  get: (recommendationId: string) => getData<Recommendation>(`recommendations/${recommendationId}`),
}

// ---------------------------------------------------------------------------
// Resource: Policies
// ---------------------------------------------------------------------------

export const policiesApi = {
  list: (orgId: string, params: PolicyListParams = {}) =>
    getDataWithMeta<Policy[]>('policies/', { query: { organization_id: orgId, ...params } }),
  get: (orgId: string, policyId: string) =>
    getData<Policy>(`policies/${policyId}`, { query: { organization_id: orgId } }),
  create: (orgId: string, payload: PolicyCreate) =>
    postData<Policy>('policies/', payload, { query: { organization_id: orgId } }),
  update: (orgId: string, policyId: string, payload: PolicyUpdate) =>
    patchData<Policy>(`policies/${policyId}`, payload, { query: { organization_id: orgId } }),
  archive: (orgId: string, policyId: string) =>
    deleteData(`policies/${policyId}`, { query: { organization_id: orgId } }),
}

// ---------------------------------------------------------------------------
// Resource: Precedents
// ---------------------------------------------------------------------------

export const precedentsApi = {
  search: (orgId: string, params: PrecedentSearchParams) =>
    getData<PrecedentSearchResult>('precedents/search', {
      query: { organization_id: orgId, ...params },
    }),
  listLinks: (orgId: string, caseId?: string) =>
    getData<PrecedentLinkRow[]>('precedents/', {
      query: { organization_id: orgId, case_id: caseId },
    }),

  /** Interactive precedent graph (/app/precedents/graph). Endpoint path is a
   *  best guess (`/precedents/graph`) pending the backend agent's final route. */
  graph: (orgId: string, params: Record<string, unknown> = {}) =>
    getData<PrecedentGraph>('precedents/graph', { query: { organization_id: orgId, ...params } }),

  /** "What would we usually do?" conversational interface (/app/precedents/ask). */
  ask: (orgId: string, payload: PrecedentAskRequest) =>
    postData<PrecedentAskResponse>('precedents/ask', payload, {
      query: { organization_id: orgId },
    }),

  /** Conflicting memory / precedent detector (/app/precedents/contradictions). */
  contradictions: (orgId: string) =>
    getData<PrecedentContradiction[]>('precedents/contradictions', {
      query: { organization_id: orgId },
    }),
}

// ---------------------------------------------------------------------------
// Resource: Insights
// ---------------------------------------------------------------------------

export const insightsApi = {
  dashboard: (orgId: string) => getData<DashboardMetrics>('insights/dashboard', {
    query: { organization_id: orgId },
  }),
  policyDrift: (orgId: string, demoMode = false) =>
    getData<PolicyDriftFinding[] | InsightsGenericResponse>('insights/policy-drift', {
      query: { organization_id: orgId, demo_mode: demoMode || undefined },
    }),
  repeatedExceptions: (orgId: string) =>
    getData<RepeatedExceptionPattern[]>('insights/repeated-exceptions', {
      query: { organization_id: orgId },
    }),
  /** Generic helper for the remaining /insights/* endpoints whose response
   *  shapes are still being finalized by the backend agent (root-causes,
   *  consistency, outcomes, success, budgets, benchmarks, memory-health,
   *  provider-usage). Pass the path segment after `/insights/`. */
  generic: (orgId: string, segment: string, params: Record<string, unknown> = {}) =>
    getData<InsightsGenericResponse>(`insights/${segment}`, {
      query: { organization_id: orgId, ...params },
    }),
  rootCauses: (orgId: string) => insightsApi.generic(orgId, 'root-causes'),
  consistency: (orgId: string) => insightsApi.generic(orgId, 'consistency'),
  outcomes: (orgId: string) => insightsApi.generic(orgId, 'outcomes'),
  success: (orgId: string) => insightsApi.generic(orgId, 'success'),
  budgets: (orgId: string) => insightsApi.generic(orgId, 'budgets'),
  benchmarks: (orgId: string) => insightsApi.generic(orgId, 'benchmarks'),
  memoryHealth: (orgId: string) => insightsApi.generic(orgId, 'memory-health'),
  providerUsage: (orgId: string) => insightsApi.generic(orgId, 'provider-usage'),
}

// ---------------------------------------------------------------------------
// Resource: Training
// ---------------------------------------------------------------------------

export const trainingApi = {
  listScenarios: () => getData<TrainingScenario[]>('training/scenarios'),
  runScenario: (orgId: string, scenarioId: string) =>
    postData<TrainingScenarioRunResult>(`training/scenarios/${scenarioId}/run`, undefined, {
      query: { organization_id: orgId },
    }),
  /** Best-guess endpoint for /app/training/history pending backend route. */
  history: (orgId: string) =>
    getData<TrainingHistoryEntry[]>('training/history', { query: { organization_id: orgId } }),
}

// ---------------------------------------------------------------------------
// Resource: Memory (Hindsight Retain / Recall / Reflect)
// ---------------------------------------------------------------------------

export const memoryApi = {
  retain: (orgId: string, payload: RetainRequest) =>
    postData<JsonObject>('memory/retain', payload, { query: { organization_id: orgId } }),
  recall: (orgId: string, payload: RecallRequest) =>
    postData<RecallResponse>('memory/recall', payload, { query: { organization_id: orgId } }),
  reflect: (orgId: string, payload: ReflectRequest) =>
    postData<ReflectResponse>('memory/reflect', payload, { query: { organization_id: orgId } }),
}

// ---------------------------------------------------------------------------
// Resource: Voice
// ---------------------------------------------------------------------------

export const voiceApi = {
  listVoices: () => getData<JsonObject>('voice/voices'),
  /** Streams audio (audio/mpeg) — returns the raw Response for the caller
   *  to pipe into an <audio> element / MediaSource. */
  synthesize: async (payload: VoiceSynthesizeRequest): Promise<Response> => {
    const token = await getAccessToken()
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }
    if (token) headers.Authorization = `Bearer ${token}`
    const response = await fetch(buildUrl('/api/v1/voice/synthesize'), {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    })
    if (!response.ok) {
      const text = await response.text()
      throw new ApiError(text || `Request failed with status ${response.status}`, response.status, null, response.url)
    }
    return response
  },
  /** Best-guess endpoints for /app/voice sessions pending backend routes. */
  listSessions: (orgId: string) =>
    getData<VoiceSession[]>('voice/sessions', { query: { organization_id: orgId } }),
  getSession: (orgId: string, sessionId: string) =>
    getData<VoiceSession>(`voice/sessions/${sessionId}`, { query: { organization_id: orgId } }),
  createSession: (orgId: string, payload: VoiceSessionRequest = {}) =>
    postData<VoiceSession>('voice/sessions', payload, { query: { organization_id: orgId } }),
}

// Re-export VoiceVoice type usage to avoid unused-import lint errors when
// consumers only need the type via voiceApi.listVoices().
export type { VoiceVoice }

// ---------------------------------------------------------------------------
// Resource: Admin
// ---------------------------------------------------------------------------

export const adminApi = {
  listOrganizations: (params: ListParams = {}) =>
    getDataWithMeta<AdminOrganizationList>('admin/organizations', { query: params }),
  listUsers: (params: ListParams = {}) =>
    getDataWithMeta<Profile[]>('admin/users', { query: params }),
  stats: () => getData<AdminStats>('admin/stats'),
  /** Best-guess endpoint for /app/admin/system-health pending backend route. */
  systemHealth: () => getData<SystemHealthStatus>('admin/system-health'),
}

// ---------------------------------------------------------------------------
// Resource: Notifications
// ---------------------------------------------------------------------------

export const notificationsApi = {
  list: (orgId?: string) =>
    getData<NotificationItem[]>('notifications', {
      query: orgId ? { organization_id: orgId } : undefined,
    }),
  markRead: (notificationId: string) =>
    request<{ message: string; data?: { id: string } }>(`notifications/${notificationId}/read`, {
      method: 'POST',
    }),
}

// ---------------------------------------------------------------------------
// Resource: OpenClaw integration
// ---------------------------------------------------------------------------

export const openclawApi = {
  status: () => getData<{ enabled: boolean; status: string }>('integrations/openclaw/status'),
  disable: () => request<MessageResponse>('integrations/openclaw/disable', { method: 'POST' }),
  /** Best-guess endpoints for OpenClaw sessions/activity pending backend routes. */
  listSessions: (orgId: string) =>
    getData<JsonObject[]>('integrations/openclaw/sessions', { query: { organization_id: orgId } }),
  listActivity: (orgId: string) =>
    getData<JsonObject[]>('integrations/openclaw/activity', { query: { organization_id: orgId } }),
}

// ---------------------------------------------------------------------------
// Resource: Demo / Replay
// ---------------------------------------------------------------------------

export const demoApi = {
  /** Best-guess endpoints for demo launcher/status/reset pending backend routes. */
  status: () => getData<DemoStatus>('demo/status'),
  reset: () => postData<DemoResetResponse>('demo/reset'),
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

export const healthApi = {
  check: () => request<JsonObject>('health', { method: 'GET' }),
}

// Re-export error type for convenience
export { ApiError }
