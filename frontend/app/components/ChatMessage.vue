<script setup lang="ts">
import type { Citation } from '~/services/chat'

interface SourceGroup {
  filename: string
  chunks: Citation[]
}

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

const renderedHtml = computed(() =>
  props.role === 'assistant' && props.text ? renderMarkdown(props.text) : '',
)

const groupedSources = computed<SourceGroup[]>(() => {
  const buckets = new Map<string, SourceGroup>()
  for (const c of props.sources ?? []) {
    const existing = buckets.get(c.filename)
    if (existing) {
      existing.chunks.push(c)
    } else {
      buckets.set(c.filename, { filename: c.filename, chunks: [c] })
    }
  }
  return [...buckets.values()]
})

const visibleGroups = computed(() =>
  groupedSources.value.slice(0, MAX_VISIBLE_SOURCES),
)
const hiddenGroups = computed(() =>
  groupedSources.value.slice(MAX_VISIBLE_SOURCES),
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

function chunkRange(c: Citation) {
  return c.line_start ? `lines ${c.line_start}–${c.line_end}` : ''
}

function groupTitle(g: SourceGroup) {
  const n = g.chunks.length
  return n > 1 ? `${g.filename} · ${n} chunks` : g.filename
}
</script>

<template>
  <div
    class="flex flex-col"
    :class="role === 'user' ? 'items-end' : 'items-start'"
  >
    <div
      class="max-w-[80%] rounded-lg px-3 py-2 text-sm break-words"
      :class="
        role === 'user'
          ? 'bg-accent text-accent-fg whitespace-pre-wrap'
          : 'border border-border bg-surface text-text'
      "
    >
      <template v-if="text">
        <div
          v-if="role === 'assistant'"
          class="markdown"
          v-html="renderedHtml"
        />
        <span v-else>{{ text }}</span>
      </template>
      <span v-else class="typing inline-flex items-center gap-1" aria-label="Loading">
        <span class="typing-dot" />
        <span class="typing-dot" />
        <span class="typing-dot" />
      </span>
    </div>

    <button
      v-if="role === 'user' && text"
      type="button"
      class="mt-1 inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-xs text-muted hover:bg-surface-2 hover:text-text"
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
      v-if="role === 'assistant' && groupedSources.length"
      class="mt-1 w-full max-w-[80%]"
    >
      <TransitionGroup
        name="source"
        tag="div"
        class="flex items-center gap-1"
      >
        <button
          v-for="(g, i) in visibleGroups"
          :key="`v-${g.filename}`"
          type="button"
          class="inline-flex max-w-[14rem] items-center gap-1 truncate rounded-md border border-border bg-surface px-2 py-1 text-xs text-muted hover:bg-surface-2 hover:text-text"
          :class="open === i ? 'bg-surface-2 text-text' : ''"
          :title="groupTitle(g)"
          @click="toggle(i)"
        >
          <Icon name="lucide:file-text" class="h-3 w-3 shrink-0" />
          <span class="truncate">{{ g.filename }}</span>
          <span
            v-if="g.chunks.length > 1"
            class="rounded bg-surface-2 px-1 text-[0.65rem] text-muted"
          >
            {{ g.chunks.length }}
          </span>
        </button>
        <button
          v-if="hiddenGroups.length"
          key="more"
          type="button"
          class="rounded-md border border-border bg-surface px-2 py-1 text-xs hover:bg-surface-2"
          :class="
            showMore ? 'bg-surface-2 text-text' : 'text-muted'
          "
          :title="
            showMore
              ? 'Hide extra sources'
              : `Show ${hiddenGroups.length} more`
          "
          :aria-expanded="showMore"
          @click="toggleMore"
        >
          {{ showMore ? '−' : '+' }}{{ hiddenGroups.length }}
        </button>
      </TransitionGroup>

      <Transition name="more">
        <div
          v-if="showMore && hiddenGroups.length"
          class="mt-1 space-y-0.5 rounded-md border border-border bg-surface p-1"
        >
          <button
            v-for="(g, k) in hiddenGroups"
            :key="`h-${g.filename}`"
            type="button"
            class="flex w-full items-center gap-1 rounded px-2 py-1 text-left text-xs text-muted hover:bg-surface-2 hover:text-text"
            :class="open === MAX_VISIBLE_SOURCES + k ? 'bg-surface-2 text-text' : ''"
            :title="groupTitle(g)"
            @click="toggle(MAX_VISIBLE_SOURCES + k)"
          >
            <Icon name="lucide:file-text" class="h-3 w-3 shrink-0" />
            <span class="truncate">{{ g.filename }}</span>
            <span
              v-if="g.chunks.length > 1"
              class="ml-auto rounded bg-surface-2 px-1 text-[0.65rem] text-muted"
            >
              {{ g.chunks.length }}
            </span>
          </button>
        </div>
      </Transition>

      <div
        v-if="open !== null && groupedSources[open]"
        class="mt-1 space-y-2 rounded-md border border-border bg-surface-2 p-2 text-xs text-text"
      >
        <div
          v-for="(c, ci) in groupedSources[open].chunks"
          :key="`c-${ci}`"
          class="space-y-1"
        >
          <p v-if="chunkRange(c)" class="text-[0.7rem] text-muted">
            {{ chunkRange(c) }}
          </p>
          <pre class="max-h-40 overflow-auto whitespace-pre-wrap">{{ c.excerpt }}</pre>
        </div>
      </div>
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
