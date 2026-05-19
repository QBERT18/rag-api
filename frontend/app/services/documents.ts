const API = 'http://localhost:8000'

export interface Document {
  filename: string
  chunks_count: number
}

export interface UploadResult {
  filename: string
  chunks_added: number
}

export function listDocuments(): Promise<Document[]> {
  return $fetch<Document[]>(`${API}/documents`)
}

export function uploadDocument(file: File): Promise<UploadResult> {
  const form = new FormData()
  form.append('file', file)
  return $fetch<UploadResult>(`${API}/documents`, {
    method: 'POST',
    body: form,
  })
}

export function deleteDocument(filename: string): Promise<void> {
  return $fetch(`${API}/documents/${encodeURIComponent(filename)}`, {
    method: 'DELETE',
  })
}

export function clearAll(): Promise<void> {
  return $fetch(`${API}/documents`, { method: 'DELETE' })
}
