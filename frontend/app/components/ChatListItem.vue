<script setup lang="ts">
import type { Chat } from '~/services/chat'

const props = defineProps<{
  chat: Chat
  active: boolean
}>()

const emit = defineEmits<{
  (e: 'select', id: number): void
  (e: 'rename', id: number, title: string): void
  (e: 'delete', id: number): void
}>()

const menuOpen = ref(false)
const editing = ref(false)
const draft = ref(props.chat.title)
const inputRef = ref<HTMLInputElement | null>(null)

watch(
  () => props.chat.title,
  (t) => {
    if (!editing.value) draft.value = t
  },
)

function startRename() {
  draft.value = props.chat.title
  editing.value = true
  menuOpen.value = false
  nextTick(() => inputRef.value?.focus())
}

function commitRename() {
  const next = draft.value.trim()
  editing.value = false
  if (next && next !== props.chat.title) emit('rename', props.chat.id, next)
  else draft.value = props.chat.title
}

function cancelRename() {
  editing.value = false
  draft.value = props.chat.title
}

function onDelete() {
  menuOpen.value = false
  if (window.confirm(`Delete "${props.chat.title}"?`)) {
    emit('delete', props.chat.id)
  }
}

function onClick() {
  if (editing.value) return
  emit('select', props.chat.id)
}
</script>

<template>
  <li
    class="group relative flex items-center gap-1 px-2 py-1.5 text-sm"
    :class="
      active ? 'bg-slate-100 text-slate-900' : 'text-slate-700 hover:bg-slate-50'
    "
  >
    <button
      v-if="!editing"
      type="button"
      class="min-w-0 flex-1 truncate text-left"
      :title="chat.title"
      @click="onClick"
    >
      {{ chat.title }}
    </button>
    <input
      v-else
      ref="inputRef"
      v-model="draft"
      type="text"
      class="min-w-0 flex-1 rounded border border-slate-300 px-1 py-0.5 text-sm focus:border-slate-500 focus:outline-none"
      @keydown.enter.prevent="commitRename"
      @keydown.escape.prevent="cancelRename"
      @blur="commitRename"
    />

    <button
      v-if="!editing"
      type="button"
      class="rounded px-1 text-slate-400 opacity-0 hover:bg-slate-200 hover:text-slate-700 group-hover:opacity-100"
      :class="{ 'opacity-100': menuOpen }"
      title="More"
      @click.stop="menuOpen = !menuOpen"
    >
      ⋯
    </button>

    <div
      v-if="menuOpen && !editing"
      class="absolute right-1 top-full z-10 mt-0.5 w-32 rounded-md border border-slate-200 bg-white py-1 text-xs shadow-md"
      @click.stop
    >
      <button
        type="button"
        class="block w-full px-2 py-1 text-left text-slate-700 hover:bg-slate-50"
        @click="startRename"
      >
        Rename
      </button>
      <button
        type="button"
        class="block w-full px-2 py-1 text-left text-red-600 hover:bg-red-50"
        @click="onDelete"
      >
        Delete
      </button>
    </div>
  </li>
</template>
