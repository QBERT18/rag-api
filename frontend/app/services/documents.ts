const apiBase = () => useRuntimeConfig().public.apiBase
const NGROK_HEADERS = { 'ngrok-skip-browser-warning': 'true' }

export interface Document {
  filename: string
  chunks_count: number
}

export interface UploadResult {
  filename: string
  chunks_added: number
}

export function listDocuments(workspaceId: string): Promise<Document[]> {
  return $fetch<Document[]>(`${apiBase()}/workspaces/${workspaceId}/documents`, {
    headers: NGROK_HEADERS,
  })
}

export function uploadDocument(
  workspaceId: string,
  file: File,
): Promise<UploadResult> {
  const form = new FormData()
  form.append('file', file)
  return $fetch<UploadResult>(`${apiBase()}/workspaces/${workspaceId}/documents`, {
    method: 'POST',
    body: form,
    headers: NGROK_HEADERS,
  })
}

export function deleteDocument(
  workspaceId: string,
  filename: string,
): Promise<void> {
  return $fetch(
    `${apiBase()}/workspaces/${workspaceId}/documents/${encodeURIComponent(filename)}`,
    { method: 'DELETE', headers: NGROK_HEADERS },
  )
}

export function clearAll(workspaceId: string): Promise<void> {
  return $fetch(`${apiBase()}/workspaces/${workspaceId}/documents`, {
    method: 'DELETE',
    headers: NGROK_HEADERS,
  })
}
