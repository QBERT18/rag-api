<script setup lang="ts">
import {
  clearAll,
  deleteDocument,
  listDocuments,
  uploadDocument,
  type Document,
} from '~/services/documents'

const props = defineProps<{ workspaceId: string }>()

type PendingState = 'queued' | 'uploading' | 'error'

interface PendingUpload {
  id: number
  file: File
  name: string
  state: PendingState
  error?: string
}

const docs = ref<Document[]>([])
const pending = ref<PendingUpload[]>([])
const error = ref<string | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const query = ref('')

let nextId = 1
let working = false
const queue: number[] = []

const filteredDocs = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return docs.value
  return docs.value.filter((d) => d.filename.toLowerCase().includes(q))
})

async function refresh() {
  try {
    docs.value = await listDocuments(props.workspaceId)
  } catch (e) {
    error.value = (e as Error).message
  }
}

function enqueue(file: File) {
  const row: PendingUpload = {
    id: nextId++,
    file,
    name: file.name,
    state: 'queued',
  }
  pending.value.push(row)
  queue.push(row.id)
}

async function drain() {
  if (working) return
  working = true
  try {
    while (queue.length) {
      const id = queue.shift()!
      const row = pending.value.find((p) => p.id === id)
      if (!row) continue
      row.state = 'uploading'
      row.error = undefined
      try {
        await uploadDocument(props.workspaceId, row.file)
        pending.value = pending.value.filter((p) => p.id !== id)
        await refresh()
      } catch (e) {
        row.state = 'error'
        row.error = (e as Error).message
      }
    }
  } finally {
    working = false
  }
}

function onPick(event: Event) {
  const target = event.target as HTMLInputElement
  const files = Array.from(target.files ?? [])
  if (fileInput.value) fileInput.value.value = ''
  if (!files.length) return
  error.value = null
  for (const f of files) enqueue(f)
  drain()
}

function retry(id: number) {
  const row = pending.value.find((p) => p.id === id)
  if (!row || row.state === 'uploading') return
  row.state = 'queued'
  row.error = undefined
  queue.push(id)
  drain()
}

function dismiss(id: number) {
  pending.value = pending.value.filter((p) => p.id !== id)
  const qi = queue.indexOf(id)
  if (qi >= 0) queue.splice(qi, 1)
}

async function onDelete(filename: string) {
  try {
    await deleteDocument(props.workspaceId, filename)
    await refresh()
  } catch (e) {
    error.value = (e as Error).message
  }
}

async function onClearAll() {
  if (!docs.value.length) return
  try {
    await clearAll(props.workspaceId)
    await refresh()
  } catch (e) {
    error.value = (e as Error).message
  }
}

onMounted(refresh)
watch(() => props.workspaceId, () => {
  docs.value = []
  pending.value = []
  queue.length = 0
  query.value = ''
  void refresh()
})
</script>

<template>
  <div class="flex h-full flex-col">
    <header class="border-b border-border p-4">
      <h2 class="text-sm font-semibold text-text">Documents</h2>
    </header>

    <div class="border-b border-border p-4">
      <label
        class="block cursor-pointer rounded-md border border-dashed border-border bg-surface-2 px-3 py-4 text-center text-sm text-muted transition hover:border-accent hover:text-text"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".txt,.md,.pdf,.docx,.html,.htm,.csv,.json"
          multiple
          class="hidden"
          @change="onPick"
        />
        <Icon name="lucide:upload" class="mr-1 inline h-4 w-4 align-[-2px]" />
        Click to upload (.txt, .md, .pdf, .docx, .html, .csv, .json)
      </label>
      <p v-if="error" class="mt-2 text-xs text-danger">{{ error }}</p>
    </div>

    <div v-if="docs.length || query" class="border-b border-border p-3">
      <SearchBox v-model="query" placeholder="Search documents" />
    </div>

    <ul class="flex-1 overflow-y-auto">
      <li
        v-for="p in pending"
        :key="`pending-${p.id}`"
        class="flex items-center justify-between border-b border-border px-4 py-2 text-sm"
      >
        <div class="min-w-0 flex-1">
          <p class="truncate text-text">{{ p.name }}</p>
          <p
            class="text-xs"
            :class="p.state === 'error' ? 'text-danger' : 'text-muted'"
          >
            <span v-if="p.state === 'queued'">Queued…</span>
            <span
              v-else-if="p.state === 'uploading'"
              class="inline-flex items-center gap-1"
            >
              <span
                class="inline-block h-2 w-2 animate-pulse rounded-full bg-accent"
              />
              Uploading…
            </span>
            <span v-else>Failed: {{ p.error }}</span>
          </p>
        </div>
        <div class="ml-2 flex gap-1 text-xs">
          <button
            v-if="p.state === 'error'"
            type="button"
            class="rounded px-2 py-1 text-muted hover:bg-surface-2 hover:text-text"
            @click="retry(p.id)"
          >
            Retry
          </button>
          <button
            v-if="p.state !== 'uploading'"
            type="button"
            class="rounded px-2 py-1 text-muted hover:bg-[var(--color-danger-soft)] hover:text-danger"
            @click="dismiss(p.id)"
          >
            Remove
          </button>
        </div>
      </li>

      <li
        v-if="!docs.length && !pending.length"
        class="p-4 text-sm text-muted"
      >
        No documents yet.
      </li>
      <li
        v-else-if="!filteredDocs.length && query"
        class="p-4 text-sm text-muted"
      >
        No documents match “{{ query }}”.
      </li>

      <li
        v-for="doc in filteredDocs"
        :key="`doc-${doc.filename}`"
        class="flex items-center justify-between border-b border-border px-4 py-2 text-sm"
      >
        <div class="flex min-w-0 flex-1 items-center gap-2">
          <Icon name="lucide:file-text" class="h-4 w-4 shrink-0 text-muted" />
          <div class="min-w-0">
            <p class="truncate text-text">{{ doc.filename }}</p>
            <p class="text-xs text-muted">{{ doc.chunks_count }} chunks</p>
          </div>
        </div>
        <button
          type="button"
          class="ml-2 rounded px-2 py-1 text-xs text-muted hover:bg-[var(--color-danger-soft)] hover:text-danger"
          @click="onDelete(doc.filename)"
        >
          Delete
        </button>
      </li>
    </ul>

    <footer v-if="docs.length" class="border-t border-border p-3">
      <button
        type="button"
        class="w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-muted hover:bg-surface-2 hover:text-text"
        @click="onClearAll"
      >
        Clear all
      </button>
    </footer>
  </div>
</template>
