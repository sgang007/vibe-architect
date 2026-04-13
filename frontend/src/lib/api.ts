const API_BASE = '/api/v1'

export async function createSession(): Promise<{
  session_id: string
  first_question: string
  quick_replies: string[]
  phase: string
}> {
  const res = await fetch(`${API_BASE}/sessions`, { method: 'POST' })
  if (!res.ok) throw new Error('Failed to create session')
  return res.json()
}

export async function getSession(sessionId: string) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`)
  if (!res.ok) throw new Error('Session not found')
  return res.json()
}

export async function generatePreview(sessionId: string): Promise<{
  screens: Array<{ id: string; name: string; purpose: string; svg: string }>
  user_flows: Array<{ persona_id: string; persona_name: string; node_count: number }>
  complexity: {
    tier: 'simple' | 'moderate' | 'complex'
    screen_count: number
    feature_count: number
    effort_weeks: string
    scope_reduction_suggestions: string[]
  }
}> {
  const res = await fetch(`${API_BASE}/preview/${sessionId}`, { method: 'POST' })
  if (!res.ok) throw new Error('Preview generation failed')
  return res.json()
}

export async function compilePrompt(
  sessionId: string,
  platform: string,
): Promise<{ prompt: string; token_estimate: number }> {
  const res = await fetch(`${API_BASE}/compile/${sessionId}/${platform}`, { method: 'POST' })
  if (!res.ok) {
    if (res.status === 429) {
      throw new Error('AI rate limit reached — please wait a moment and try again')
    }
    const body = await res.json().catch(() => ({}))
    throw new Error((body as { detail?: string }).detail || 'Compilation failed')
  }
  return res.json()
}

// SSE via fetch (supports POST)
export async function submitAnswerSSE(
  sessionId: string,
  answer: string,
  onEvent: (event: string, data: unknown) => void,
): Promise<void> {
  const res = await fetch(`${API_BASE}/enrichment/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, answer }),
  })
  if (!res.ok || !res.body) throw new Error('SSE stream failed')
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  const parseAndDispatch = (raw: string) => {
    const lines = raw.split('\n')
    let eventType = 'message'
    let dataStr = ''
    for (const line of lines) {
      if (line.startsWith('event: ')) eventType = line.slice(7).trim()
      if (line.startsWith('data: ')) dataStr = line.slice(6).trim()
    }
    if (dataStr) {
      try {
        onEvent(eventType, JSON.parse(dataStr))
      } catch {
        onEvent(eventType, dataStr)
      }
    }
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) {
      // Flush any remaining data in the buffer that didn't end with \n\n
      // (e.g. the final `extracted` event when the stream closes immediately after)
      const remaining = buffer.trim()
      if (remaining) parseAndDispatch(remaining)
      break
    }
    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''
    for (const part of parts) {
      if (part.trim()) parseAndDispatch(part)
    }
  }
}
