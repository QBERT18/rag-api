<script setup lang="ts">
import { getWorkspace, type Workspace } from '~/services/workspaces'

const route = useRoute()
const router = useRouter()

const workspaceId = computed(() => String(route.params.id))
const workspace = ref<Workspace | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

const { width, dragging, containerRef, startDrag } = useResizablePane({
  storageKey: 'rag-docs-pane-width',
  initial: 320,
  min: 240,
  minOther: 360,
})

async function load(id: string) {
  loading.value = true
  error.value = null
  try {
    workspace.value = await getWorkspace(id)
  } catch (e) {
    workspace.value = null
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}

onMounted(() => load(workspaceId.value))
watch(workspaceId, (id) => load(id))

function goHome() {
  router.push('/')
}
</script>

<template>
  <div class="flex h-screen flex-col bg-bg text-text">
    <AppHeader tight>
      <template #left>
        <button
          type="button"
          class="inline-flex items-center gap-1.5 rounded-md border border-border bg-surface px-2.5 py-1.5 text-xs text-muted hover:bg-surface-2 hover:text-text"
          @click="goHome"
        >
          <Icon name="lucide:arrow-left" class="h-3.5 w-3.5" />
          Workspaces
        </button>
      </template>
    </AppHeader>

    <p v-if="loading" class="p-6 text-sm text-muted">Loading workspace…</p>
    <div
      v-else-if="error || !workspace"
      class="flex flex-1 flex-col items-center justify-center gap-3 p-6 text-sm text-muted"
    >
      <p>{{ error ?? 'Workspace not found.' }}</p>
      <button
        type="button"
        class="rounded-md border border-border bg-surface px-3 py-1 text-xs text-muted hover:bg-surface-2 hover:text-text"
        @click="goHome"
      >
        Back to workspaces
      </button>
    </div>

    <div v-else ref="containerRef" class="flex min-h-0 flex-1">
      <aside
        class="shrink-0 border-r border-border bg-surface"
        :style="{ width: `${width}px` }"
      >
        <DocumentsPane :workspace-id="workspace.id" />
      </aside>
      <div
        class="group relative w-1 shrink-0 cursor-col-resize bg-border transition-colors hover:bg-accent"
        :class="dragging ? 'bg-accent' : ''"
        role="separator"
        aria-orientation="vertical"
        title="Drag to resize"
        @pointerdown="startDrag"
      >
        <span class="absolute inset-y-0 -left-1 -right-1" />
      </div>
      <main class="min-w-0 flex-1 bg-bg">
        <ChatPane :workspace-id="workspace.id" :workspace-name="workspace.name" />
      </main>
    </div>
  </div>
</template>
