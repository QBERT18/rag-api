<script setup lang="ts">
import type { Citation } from '~/services/chat'

const MAX_VISIBLE_SOURCES = 2

const props = defineProps<{
  role: 'user' | 'assistant'
  text: string
  sources?: Citation[]
}>()

const emit = defineEmits<{
  (e: 'reask', text: string): void
}>()

const open = ref<number | null>(null)
const showMore = ref(false)

const visibleSources = computed(() =>
  (props.sources ?? []).slice(0, MAX_VISIBLE_SOURCES),
)
const hiddenSources = computed(() =>
  (props.sources ?? []).slice(MAX_VISIBLE_SOURCES),
)

function toggle(i: number) {
  open.value = open.value === i ? null : i
}

function toggleMore() {
  showMore.value = !showMore.value
  if (
    !showMore.value &&
    open.value !== null &&
    open.value >= MAX_VISIBLE_SOURCES
  ) {
    open.value = null
  }
}

function chipTitle(s: Citation) {
  return s.line_start
    ? `${s.filename} · lines ${s.line_start}–${s.line_end}`
    : s.filename
}
</script>

<template>
  <div
    class="flex flex-col"
    :class="role === 'user' ? 'items-end' : 'items-start'"
  >
    <div
      class="max-w-[80%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap break-words"
      :class="
        role === 'user'
          ? 'bg-slate-900 text-white'
          : 'bg-slate-100 text-slate-900'
      "
    >
      <span v-if="text">{{ text }}</span>
      <span v-else class="typing inline-flex items-center gap-1" aria-label="Loading">
        <span class="typing-dot" />
        <span class="typing-dot" />
        <span class="typing-dot" />
      </span>
    </div>

    <button
      v-if="role === 'user' && text"
      type="button"
      class="mt-1 inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-xs text-slate-400 hover:bg-slate-100 hover:text-slate-700"
      title="Ask this again"
      @click="emit('reask', text)"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-3 w-3"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <polyline points="23 4 23 10 17 10" />
        <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
      </svg>
      Re-ask
    </button>

    <div
      v-if="role === 'assistant' && sources?.length"
      class="mt-1 w-full max-w-[80%]"
    >
      <TransitionGroup
        name="source"
        tag="div"
        class="flex items-center gap-1"
      >
        <button
          v-for="(s, i) in visibleSources"
          :key="`v-${i}`"
          type="button"
          class="max-w-[12rem] truncate rounded-md border border-slate-200 px-2 py-1 text-xs text-slate-600 hover:bg-slate-50"
          :title="chipTitle(s)"
          @click="toggle(i)"
        >
          📄 {{ s.filename }}
        </button>
        <button
          v-if="hiddenSources.length"
          key="more"
          type="button"
          class="rounded-md border border-slate-200 px-2 py-1 text-xs hover:bg-slate-50"
          :class="
            showMore ? 'bg-slate-100 text-slate-700' : 'text-slate-500'
          "
          :title="
            showMore
              ? 'Hide extra sources'
              : `Show ${hiddenSources.length} more`
          "
          :aria-expanded="showMore"
          @click="toggleMore"
        >
          {{ showMore ? '−' : '+' }}{{ hiddenSources.length }}
        </button>
      </TransitionGroup>

      <Transition name="more">
        <div
          v-if="showMore && hiddenSources.length"
          class="mt-1 space-y-0.5 rounded-md border border-slate-200 bg-white p-1"
        >
          <button
            v-for="(s, k) in hiddenSources"
            :key="`h-${k}`"
            type="button"
            class="block w-full truncate rounded px-2 py-1 text-left text-xs text-slate-600 hover:bg-slate-50"
            :title="chipTitle(s)"
            @click="toggle(MAX_VISIBLE_SOURCES + k)"
          >
            📄 {{ s.filename }}
            <span v-if="s.line_start" class="text-slate-400">
              · lines {{ s.line_start }}–{{ s.line_end }}
            </span>
          </button>
        </div>
      </Transition>

      <pre
        v-if="open !== null && sources?.[open]"
        class="mt-1 max-h-40 overflow-auto rounded-md bg-slate-50 p-2 text-xs whitespace-pre-wrap text-slate-700"
      >{{ sources?.[open]?.excerpt }}</pre>
    </div>
  </div>
</template>

<style scoped>
.source-enter-active {
  transition:
    opacity 520ms ease-out,
    transform 520ms ease-out;
}
.source-enter-from {
  opacity: 0;
  transform: translateY(-4px);
}

.more-enter-active,
.more-leave-active {
  transition:
    opacity 220ms ease-out,
    transform 220ms ease-out;
}
.more-enter-from,
.more-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.typing {
  height: 1rem;
}
.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  background-color: rgb(100 116 139);
  animation: typing-bounce 1.2s ease-in-out infinite;
}
.typing-dot:nth-child(2) {
  animation-delay: 0.15s;
}
.typing-dot:nth-child(3) {
  animation-delay: 0.3s;
}
@keyframes typing-bounce {
  0%,
  60%,
  100% {
    transform: translateY(0);
    opacity: 0.35;
  }
  30% {
    transform: translateY(-4px);
    opacity: 0.95;
  }
}
</style>
