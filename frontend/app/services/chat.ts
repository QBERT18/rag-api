const apiBase = () => useRuntimeConfig().public.apiBase

export interface Citation {
  filename: string
  line_start: number | null
  line_end: number | null
  excerpt: string
}

export interface StoredMessage {
  id: number
  workspace_id: string
  role: 'user' | 'assistant'
  content: string
  sources: Citation[] | null
  created_at: string
}

async function jsonRequest<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(`${apiBase()}${path}`, {
    ...init,
    headers: {
      'ngrok-skip-browser-warning': 'true',
      ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
      ...(init?.headers ?? {}),
    },
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return (await res.json()) as T
}

export function listMessages(workspaceId: string): Promise<StoredMessage[]> {
  return jsonRequest<StoredMessage[]>(`/workspaces/${workspaceId}/messages`)
}

export async function streamAsk(
  workspaceId: string,
  question: string,
  onToken: (chunk: string) => void,
  onSources: (sources: Citation[]) => void,
  onDone?: (messageId: number) => void,
  signal?: AbortSignal,
): Promise<void> {
  const url = `${apiBase()}/ask/${workspaceId}/stream?question=${encodeURIComponent(question)}`
  const res = await fetch(url, {
    signal,
    headers: { 'ngrok-skip-browser-warning': 'true' },
  })
  if (!res.ok || !res.body) {
    throw new Error(`Stream failed: ${res.status} ${res.statusText}`)
  }
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  const handleLine = (line: string) => {
    if (!line) return
    const ev = JSON.parse(line)
    if (ev.type === 'sources') onSources(ev.items as Citation[])
    else if (ev.type === 'token') onToken(ev.text as string)
    else if (ev.type === 'done') onDone?.(ev.message_id as number)
  }

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    let nl: number
    while ((nl = buffer.indexOf('\n')) !== -1) {
      const line = buffer.slice(0, nl).trim()
      buffer = buffer.slice(nl + 1)
      handleLine(line)
    }
  }
  handleLine(buffer.trim())
}
