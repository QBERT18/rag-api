<script setup lang="ts">
import { streamAsk, type Citation } from '~/services/chat'

interface Message {
  role: 'user' | 'assistant'
  text: string
  sources?: Citation[]
}

const messages = ref<Message[]>([])
const input = ref('')
const pending = ref(false)
const error = ref<string | null>(null)
const scrollRef = ref<HTMLElement | null>(null)

function scrollToBottom() {
  nextTick(() => {
    const el = scrollRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

async function onSubmit() {
  const question = input.value.trim()
  if (!question || pending.value) return

  messages.value.push({ role: 'user', text: question })
  const assistantIdx = messages.value.push({ role: 'assistant', text: '' }) - 1
  input.value = ''
  error.value = null
  pending.value = true
  scrollToBottom()

  try {
    await streamAsk(
      question,
      (chunk) => {
        messages.value[assistantIdx].text += chunk
        scrollToBottom()
      },
      (items) => {
        messages.value[assistantIdx].sources = items
        scrollToBottom()
      },
    )
  } catch (e) {
    error.value = (e as Error).message
    messages.value[assistantIdx].text = `[error] ${error.value}`
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="flex h-full flex-col">
    <header class="border-b border-slate-200 p-4">
      <h2 class="text-sm font-semibold text-slate-700">Chat</h2>
    </header>

    <div ref="scrollRef" class="flex-1 space-y-3 overflow-y-auto p-4">
      <p v-if="!messages.length" class="text-sm text-slate-400">
        Ask a question about your uploaded documents.
      </p>
      <ChatMessage
        v-for="(msg, i) in messages"
        :key="i"
        :role="msg.role"
        :text="msg.text"
        :sources="msg.sources"
      />
    </div>

    <form
      class="flex gap-2 border-t border-slate-200 p-3"
      @submit.prevent="onSubmit"
    >
      <input
        v-model="input"
        type="text"
        placeholder="Type a message…"
        class="flex-1 rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-slate-400 focus:outline-none"
        :disabled="pending"
      />
      <button
        type="submit"
        class="rounded-md bg-slate-900 px-4 py-2 text-sm text-white hover:bg-slate-800 disabled:bg-slate-400"
        :disabled="pending || !input.trim()"
      >
        {{ pending ? '…' : 'Send' }}
      </button>
    </form>
  </div>
</template>
