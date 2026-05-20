<script setup lang="ts">
import type { Workspace } from '~/services/workspaces'

const props = defineProps<{ workspace: Workspace }>()
const emit = defineEmits<{
  (e: 'open', id: string): void
  (e: 'rename', id: string, name: string): void
  (e: 'delete', id: string): void
}>()

const menuOpen = ref(false)
const editing = ref(false)
const draft = ref(props.workspace.name)
const inputRef = ref<HTMLInputElement | null>(null)

watch(
  () => props.workspace.name,
  (n) => {
    if (!editing.value) draft.value = n
  },
)

function startRename() {
  draft.value = props.workspace.name
  editing.value = true
  menuOpen.value = false
  nextTick(() => inputRef.value?.focus())
}

function commitRename() {
  const next = draft.value.trim()
  editing.value = false
  if (next && next !== props.workspace.name) {
    emit('rename', props.workspace.id, next)
  } else {
    draft.value = props.workspace.name
  }
}

function cancelRename() {
  editing.value = false
  draft.value = props.workspace.name
}

function onDelete() {
  menuOpen.value = false
  if (window.confirm(`Delete workspace "${props.workspace.name}"? Files and chat will be lost.`)) {
    emit('delete', props.workspace.id)
  }
}

function onCardClick() {
  if (editing.value || menuOpen.value) return
  emit('open', props.workspace.id)
}

const updated = computed(() => {
  const d = new Date(props.workspace.updated_at)
  return d.toLocaleString()
})
</script>

<template>
  <div
    class="group relative flex aspect-[4/3] cursor-pointer flex-col justify-between rounded-lg border border-slate-200 bg-white p-5 shadow-sm transition hover:border-slate-400 hover:shadow-md"
    @click="onCardClick"
  >
    <div class="min-w-0">
      <input
        v-if="editing"
        ref="inputRef"
        v-model="draft"
        type="text"
        class="w-full rounded border border-slate-300 px-2 py-1 text-base font-medium focus:border-slate-500 focus:outline-none"
        @click.stop
        @keydown.enter.prevent="commitRename"
        @keydown.escape.prevent="cancelRename"
        @blur="commitRename"
      />
      <h3
        v-else
        class="truncate text-base font-medium text-slate-900"
        :title="workspace.name"
      >
        {{ workspace.name }}
      </h3>
    </div>

    <p class="text-xs text-slate-400">Updated {{ updated }}</p>

    <button
      v-if="!editing"
      type="button"
      class="absolute right-2 top-2 rounded p-1 text-slate-400 opacity-0 hover:bg-slate-100 hover:text-slate-700 group-hover:opacity-100"
      :class="{ 'opacity-100': menuOpen }"
      title="More"
      @click.stop="menuOpen = !menuOpen"
    >
      ⋯
    </button>

    <div
      v-if="menuOpen && !editing"
      class="absolute right-2 top-9 z-10 w-32 rounded-md border border-slate-200 bg-white py-1 text-xs shadow-md"
      @click.stop
    >
      <button
        type="button"
        class="block w-full px-3 py-1.5 text-left text-slate-700 hover:bg-slate-50"
        @click="startRename"
      >
        Rename
      </button>
      <button
        type="button"
        class="block w-full px-3 py-1.5 text-left text-red-600 hover:bg-red-50"
        @click="onDelete"
      >
        Delete
      </button>
    </div>
  </div>
</template>
