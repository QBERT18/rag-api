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
const menuRef = ref<HTMLElement | null>(null)
const menuBtnRef = ref<HTMLElement | null>(null)

watch(
  () => props.workspace.name,
  (n) => {
    if (!editing.value) draft.value = n
  },
)

function onDocPointerDown(event: PointerEvent) {
  if (!menuOpen.value) return
  const target = event.target as Node | null
  if (menuRef.value?.contains(target) || menuBtnRef.value?.contains(target)) return
  menuOpen.value = false
}

watch(menuOpen, (open) => {
  if (open) {
    document.addEventListener('pointerdown', onDocPointerDown, true)
  } else {
    document.removeEventListener('pointerdown', onDocPointerDown, true)
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', onDocPointerDown, true)
})

const tile = computed(() => tileIndex(props.workspace.id) + 1)
const updated = computed(() => formatRelative(props.workspace.updated_at))
const docCount = computed(() => props.workspace.doc_count ?? 0)

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
  emit('delete', props.workspace.id)
}

function onClick() {
  if (editing.value) return
  if (menuOpen.value) {
    menuOpen.value = false
    return
  }
  emit('open', props.workspace.id)
}
</script>

<template>
  <div
    class="group relative flex cursor-pointer items-center gap-3 rounded-md border border-border bg-surface px-3 py-2.5 transition hover:bg-surface-2"
    @click="onClick"
  >
    <span
      class="flex h-9 w-9 shrink-0 items-center justify-center rounded-md"
      :style="{
        backgroundColor: `var(--color-tile-${tile})`,
        color: `var(--color-tile-fg-${tile})`,
      }"
    >
      <Icon name="lucide:book-open" class="h-4 w-4" />
    </span>

    <div class="min-w-0 flex-1">
      <input
        v-if="editing"
        ref="inputRef"
        v-model="draft"
        type="text"
        class="w-full rounded border border-border bg-bg px-2 py-1 text-sm text-text focus:border-accent focus:outline-none"
        @click.stop
        @keydown.enter.prevent="commitRename"
        @keydown.escape.prevent="cancelRename"
        @blur="commitRename"
      />
      <p v-else class="truncate text-sm font-medium text-text" :title="workspace.name">
        {{ workspace.name }}
      </p>
      <p class="text-xs text-muted">
        <span>{{ updated }}</span>
        <span class="px-1.5">·</span>
        <span>{{ docCount }} {{ docCount === 1 ? 'source' : 'sources' }}</span>
      </p>
    </div>

    <button
      v-if="!editing"
      ref="menuBtnRef"
      type="button"
      class="rounded p-1 text-muted opacity-0 hover:bg-surface-2 hover:text-text group-hover:opacity-100"
      :class="{ 'opacity-100': menuOpen }"
      title="More"
      @click.stop="menuOpen = !menuOpen"
    >
      <Icon name="lucide:more-horizontal" class="h-4 w-4" />
    </button>

    <div
      v-if="menuOpen && !editing"
      ref="menuRef"
      class="absolute right-2 top-11 z-10 w-32 rounded-md border border-border bg-bg py-1 text-xs shadow-md"
      @click.stop
    >
      <button
        type="button"
        class="block w-full px-3 py-1.5 text-left text-text hover:bg-surface-2"
        @click="startRename"
      >
        Rename
      </button>
      <button
        type="button"
        class="block w-full px-3 py-1.5 text-left text-danger hover:bg-[var(--color-danger-soft)]"
        @click="onDelete"
      >
        Delete
      </button>
    </div>
  </div>
</template>
