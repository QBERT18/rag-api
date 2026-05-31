const apiBase = () => useRuntimeConfig().public.apiBase

export interface Workspace {
  id: string
  name: string
  created_at: string
  updated_at: string
  doc_count?: number
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

export function listWorkspaces(): Promise<Workspace[]> {
  return jsonRequest<Workspace[]>('/workspaces')
}

export function getWorkspace(id: string): Promise<Workspace> {
  return jsonRequest<Workspace>(`/workspaces/${id}`)
}

export function createWorkspace(name: string): Promise<Workspace> {
  return jsonRequest<Workspace>('/workspaces', {
    method: 'POST',
    body: JSON.stringify({ name }),
  })
}

export function renameWorkspace(id: string, name: string): Promise<Workspace> {
  return jsonRequest<Workspace>(`/workspaces/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ name }),
  })
}

export async function deleteWorkspace(id: string): Promise<void> {
  const res = await fetch(`${apiBase()}/workspaces/${id}`, {
    method: 'DELETE',
    headers: { 'ngrok-skip-browser-warning': 'true' },
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
}
