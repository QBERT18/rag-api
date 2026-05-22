<script setup lang="ts">
import {
  listMessages as apiListMessages,
  streamAsk,
  type Citation,
  type StoredMessage,
} from '~/services/chat'

const props = defineProps<{ workspaceId: string; workspaceName: string }>()

interface UIMessage {
  role: 'user' | 'assistant'
  text: string
  sources?: Citation[]
}

const messages = ref<UIMessage[]>([])
const loadingMessages = ref(false)
const input = ref('')
const pending = ref(false)
const error = ref<string | null>(null)
const scrollRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)
let abortController: AbortController | null = null

const inputHistory = ref<string[]>([])
const historyIdx = ref(-1)
const draft = ref('')

function toUI(m: StoredMessage): UIMessage {
  return {
    role: m.role,
    text: m.content,
    sources: m.sources ?? undefined,
  }
}

async function hydrate() {
  loadingMessages.value = true
  try {
    const rows = await apiListMessages(props.workspaceId)
    messages.value = rows.map(toUI)
  } finally {
    loadingMessages.value = false
    scrollToBottom()
  }
}

onMounted(() => {
  void hydrate()
})

watch(
  () => props.workspaceId,
  () => {
    messages.value = []
    inputHistory.value = []
    historyIdx.value = -1
    draft.value = ''
    void hydrate()
  },
)

function scrollToBottom() {
  nextTick(() => {
    const el = scrollRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

function moveCursorToEnd() {
  nextTick(() => {
    const el = inputRef.value
    if (el) el.setSelectionRange(el.value.length, el.value.length)
  })
}

function pushInputHistory(text: string) {
  if (inputHistory.value[inputHistory.value.length - 1] !== text) {
    inputHistory.value.push(text)
  }
}

function onKeyDown(e: KeyboardEvent) {
  const history = inputHistory.value
  if (e.key === 'ArrowUp') {
    if (!history.length) return
    e.preventDefault()
    if (historyIdx.value === -1) {
      draft.value = input.value
      historyIdx.value = history.length - 1
    } else if (historyIdx.value > 0) {
      historyIdx.value -= 1
    } else {
      return
    }
    input.value = history[historyIdx.value]!
    moveCursorToEnd()
  } else if (e.key === 'ArrowDown') {
    if (historyIdx.value === -1) return
    e.preventDefault()
    if (historyIdx.value < history.length - 1) {
      historyIdx.value += 1
      input.value = history[historyIdx.value]!
    } else {
      historyIdx.value = -1
      input.value = draft.value
    }
    moveCursorToEnd()
  }
}

function onInput() {
  const history = inputHistory.value
  if (
    historyIdx.value !== -1 &&
    input.value !== history[historyIdx.value]
  ) {
    historyIdx.value = -1
  }
}

const SOURCE_FIRST_DELAY_MS = 700
const SOURCE_REVEAL_MS = 260

function appendAssistantToken(token: string) {
  const last = messages.value[messages.value.length - 1]
  if (last && last.role === 'assistant') last.text += token
}

function setAssistantSources(sources: Citation[]) {
  const last = messages.value[messages.value.length - 1]
  if (last && last.role === 'assistant') last.sources = sources
}

async function ask(question: string) {
  pushInputHistory(question)
  historyIdx.value = -1
  draft.value = ''

  messages.value.push({ role: 'user', text: question })
  messages.value.push({ role: 'assistant', text: '' })
  error.value = null
  pending.value = true
  abortController = new AbortController()
  scrollToBottom()

  let pendingSources: Citation[] | null = null
  let revealed = 0
  let revealStarted = false
  let revealTimer: ReturnType<typeof setInterval> | null = null

  function revealNext() {
    if (!pendingSources) return
    if (revealed >= pendingSources.length) {
      if (revealTimer) {
        clearInterval(revealTimer)
        revealTimer = null
      }
      return
    }
    revealed += 1
    setAssistantSources(pendingSources.slice(0, revealed))
    scrollToBottom()
  }

  function startReveal() {
    if (revealStarted || !pendingSources) return
    revealStarted = true
    setTimeout(() => {
      revealNext()
      revealTimer = setInterval(revealNext, SOURCE_REVEAL_MS)
    }, SOURCE_FIRST_DELAY_MS)
  }

  const last = messages.value[messages.value.length - 1]!

  try {
    await streamAsk(
      props.workspaceId,
      question,
      (chunk) => {
        const wasEmpty = !last.text
        appendAssistantToken(chunk)
        scrollToBottom()
        if (wasEmpty) startReveal()
      },
      (items) => {
        pendingSources = items
        if (last.text) startReveal()
      },
      undefined,
      abortController.signal,
    )
  } catch (e) {
    const err = e as Error
    const aborted =
      err.name === 'AbortError' ||
      (err as unknown as { code?: number }).code === 20
    if (aborted) {
      if (!last.text) last.text = '[stopped]'
    } else {
      error.value = err.message
      last.text = `[error] ${error.value}`
    }
    startReveal()
  } finally {
    pending.value = false
    abortController = null
    if (revealTimer) {
      clearInterval(revealTimer)
      revealTimer = null
    }
  }
}

function onStop() {
  abortController?.abort()
}

async function onSubmit() {
  const question = input.value.trim()
  if (!question || pending.value) return
  input.value = ''
  await ask(question)
}

function onReask(text: string) {
  if (pending.value) return
  void ask(text)
}
</script>

<template>
  <div class="flex h-full flex-col">
    <header class="border-b border-border p-4">
      <h2 class="truncate text-sm font-semibold text-text">
        {{ workspaceName || 'Chat' }}
      </h2>
    </header>

    <div ref="scrollRef" class="flex-1 space-y-3 overflow-y-auto p-4">
      <p v-if="loadingMessages" class="text-sm text-muted">Loading…</p>
      <p
        v-else-if="!messages.length"
        class="text-sm text-muted"
      >
        Ask a question about your uploaded documents.
      </p>
      <ChatMessage
        v-for="(msg, i) in messages"
        :key="i"
        :role="msg.role"
        :text="msg.text"
        :sources="msg.sources"
        @reask="onReask"
      />
    </div>

    <form
      class="flex gap-2 border-t border-border p-3"
      @submit.prevent="onSubmit"
    >
      <input
        ref="inputRef"
        v-model="input"
        type="text"
        placeholder="Type a message…"
        class="flex-1 rounded-md border border-border bg-surface px-3 py-2 text-sm text-text placeholder:text-muted focus:border-accent focus:outline-none disabled:opacity-60"
        :disabled="pending"
        @keydown="onKeyDown"
        @input="onInput"
      />
      <button
        v-if="!pending"
        type="submit"
        class="inline-flex items-center gap-1 rounded-md bg-accent px-4 py-2 text-sm text-accent-fg transition hover:opacity-90 disabled:opacity-50"
        :disabled="!input.trim()"
      >
        <Icon name="lucide:arrow-up" class="h-4 w-4" />
        Send
      </button>
      <button
        v-else
        type="button"
        class="inline-flex items-center gap-1 rounded-md bg-danger px-4 py-2 text-sm text-white transition hover:opacity-90"
        title="Stop generation"
        @click="onStop"
      >
        <Icon name="lucide:square" class="h-4 w-4" />
        Stop
      </button>
    </form>

    <p
      v-if="error"
      class="border-t border-danger/30 bg-[var(--color-danger-soft)] px-4 py-2 text-xs text-danger"
    >
      {{ error }}
    </p>
  </div>
</template>
