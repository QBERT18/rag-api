const apiBase = () => useRuntimeConfig().public.apiBase

export interface Document {
  filename: string
  chunks_count: number
}

export interface UploadResult {
  filename: string
  chunks_added: number
}

export function listDocuments(workspaceId: string): Promise<Document[]> {
  return $fetch<Document[]>(`${apiBase()}/workspaces/${workspaceId}/documents`)
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
  })
}

export function deleteDocument(
  workspaceId: string,
  filename: string,
): Promise<void> {
  return $fetch(
    `${apiBase()}/workspaces/${workspaceId}/documents/${encodeURIComponent(filename)}`,
    { method: 'DELETE' },
  )
}

export function clearAll(workspaceId: string): Promise<void> {
  return $fetch(`${apiBase()}/workspaces/${workspaceId}/documents`, {
    method: 'DELETE',
  })
}
