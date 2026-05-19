const API = 'http://localhost:8000'

export interface Citation {
  filename: string
  line_start: number | null
  line_end: number | null
  excerpt: string
}

export async function streamAsk(
  question: string,
  onToken: (chunk: string) => void,
  onSources: (sources: Citation[]) => void,
  signal?: AbortSignal,
): Promise<void> {
  const url = `${API}/ask/stream?question=${encodeURIComponent(question)}`
  const res = await fetch(url, { signal })
  if (!res.ok || !res.body) {
    throw new Error(`Stream failed: ${res.status} ${res.statusText}`)
  }
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    let nl: number
    while ((nl = buffer.indexOf('\n')) !== -1) {
      const line = buffer.slice(0, nl).trim()
      buffer = buffer.slice(nl + 1)
      if (!line) continue
      const ev = JSON.parse(line)
      if (ev.type === 'sources') onSources(ev.items as Citation[])
      else if (ev.type === 'token') onToken(ev.text as string)
    }
  }
  const tail = buffer.trim()
  if (tail) {
    const ev = JSON.parse(tail)
    if (ev.type === 'sources') onSources(ev.items as Citation[])
    else if (ev.type === 'token') onToken(ev.text as string)
  }
}
