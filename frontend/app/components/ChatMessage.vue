<script setup lang="ts">
import type { Citation } from '~/services/chat'

defineProps<{
  role: 'user' | 'assistant'
  text: string
  sources?: Citation[]
}>()

const open = ref<number | null>(null)
function toggle(i: number) {
  open.value = open.value === i ? null : i
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
      <span v-else class="inline-block h-4 w-2 animate-pulse bg-slate-400" />
    </div>

    <div
      v-if="role === 'assistant' && sources?.length"
      class="mt-1 w-full max-w-[80%] space-y-1"
    >
      <div v-for="(s, i) in sources" :key="i" class="text-xs">
        <button
          type="button"
          class="rounded-md border border-slate-200 px-2 py-1 text-slate-600 hover:bg-slate-50"
          @click="toggle(i)"
        >
          📄 {{ s.filename }}
          <span v-if="s.line_start" class="text-slate-400">
            · lines {{ s.line_start }}–{{ s.line_end }}
          </span>
        </button>
        <pre
          v-if="open === i"
          class="mt-1 max-h-40 overflow-auto rounded-md bg-slate-50 p-2 text-slate-700 whitespace-pre-wrap"
        >{{ s.excerpt }}</pre>
      </div>
    </div>
  </div>
</template>
