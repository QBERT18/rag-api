const API = 'http://localhost:8000'

export interface Document {
  filename: string
  chunks_count: number
}

export interface UploadResult {
  filename: string
  chunks_added: number
}

export function listDocuments(workspaceId: string): Promise<Document[]> {
  return $fetch<Document[]>(`${API}/workspaces/${workspaceId}/documents`)
}

export function uploadDocument(
  workspaceId: string,
  file: File,
): Promise<UploadResult> {
  const form = new FormData()
  form.append('file', file)
  return $fetch<UploadResult>(`${API}/workspaces/${workspaceId}/documents`, {
    method: 'POST',
    body: form,
  })
}

export function deleteDocument(
  workspaceId: string,
  filename: string,
): Promise<void> {
  return $fetch(
    `${API}/workspaces/${workspaceId}/documents/${encodeURIComponent(filename)}`,
    { method: 'DELETE' },
  )
}

export function clearAll(workspaceId: string): Promise<void> {
  return $fetch(`${API}/workspaces/${workspaceId}/documents`, {
    method: 'DELETE',
  })
}
