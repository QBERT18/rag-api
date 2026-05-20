const API = 'http://localhost:8000'

export interface Citation {
  filename: string
  line_start: number | null
  line_end: number | null
  excerpt: string
}

export interface Chat {
  id: number
  title: string
  created_at: string
  updated_at: string
}

export interface StoredMessage {
  id: number
  chat_id: number
  role: 'user' | 'assistant'
  content: string
  sources: Citation[] | null
  created_at: string
}

async function jsonRequest<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: {
      ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
      ...(init?.headers ?? {}),
    },
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return (await res.json()) as T
}

export function listChats(): Promise<Chat[]> {
  return jsonRequest<Chat[]>('/chats')
}

export function createChat(title?: string): Promise<Chat> {
  return jsonRequest<Chat>('/chats', {
    method: 'POST',
    body: JSON.stringify({ title: title ?? null }),
  })
}

export function renameChat(id: number, title: string): Promise<Chat> {
  return jsonRequest<Chat>(`/chats/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ title }),
  })
}

export async function deleteChat(id: number): Promise<void> {
  const res = await fetch(`${API}/chats/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
}

export function listMessages(chatId: number): Promise<StoredMessage[]> {
  return jsonRequest<StoredMessage[]>(`/chats/${chatId}/messages`)
}

export async function streamAsk(
  chatId: number,
  question: string,
  onToken: (chunk: string) => void,
  onSources: (sources: Citation[]) => void,
  onDone?: (messageId: number) => void,
  signal?: AbortSignal,
): Promise<void> {
  const url = `${API}/ask/${chatId}/stream?question=${encodeURIComponent(question)}`
  const res = await fetch(url, { signal })
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
