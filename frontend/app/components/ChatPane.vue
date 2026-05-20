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
    )
  } catch (e) {
    error.value = (e as Error).message
    last.text = `[error] ${error.value}`
    startReveal()
  } finally {
    pending.value = false
  }
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
    <header class="border-b border-slate-200 p-4">
      <h2 class="truncate text-sm font-semibold text-slate-700">
        {{ workspaceName || 'Chat' }}
      </h2>
    </header>

    <div ref="scrollRef" class="flex-1 space-y-3 overflow-y-auto p-4">
      <p v-if="loadingMessages" class="text-sm text-slate-400">Loading…</p>
      <p
        v-else-if="!messages.length"
        class="text-sm text-slate-400"
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
      class="flex gap-2 border-t border-slate-200 p-3"
      @submit.prevent="onSubmit"
    >
      <input
        ref="inputRef"
        v-model="input"
        type="text"
        placeholder="Type a message…"
        class="flex-1 rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-slate-400 focus:outline-none disabled:bg-slate-50"
        :disabled="pending"
        @keydown="onKeyDown"
        @input="onInput"
      />
      <button
        type="submit"
        class="rounded-md bg-slate-900 px-4 py-2 text-sm text-white hover:bg-slate-800 disabled:bg-slate-400"
        :disabled="pending || !input.trim()"
      >
        {{ pending ? '…' : 'Send' }}
      </button>
    </form>

    <p v-if="error" class="border-t border-red-100 bg-red-50 px-4 py-2 text-xs text-red-700">
      {{ error }}
    </p>
  </div>
</template>
