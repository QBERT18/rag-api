<script setup lang="ts">
import { getWorkspace, type Workspace } from '~/services/workspaces'

const route = useRoute()
const router = useRouter()

const workspaceId = computed(() => String(route.params.id))
const workspace = ref<Workspace | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

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
  <div class="flex h-screen flex-col bg-white text-slate-900">
    <header class="flex items-center justify-between border-b border-slate-200 px-4 py-2">
      <button
        type="button"
        class="rounded-md border border-slate-200 px-3 py-1 text-xs text-slate-600 hover:bg-slate-50"
        @click="goHome"
      >
        ← Workspaces
      </button>
      <h1 class="truncate text-sm font-semibold text-slate-700">
        {{ workspace?.name ?? '' }}
      </h1>
      <span class="w-24" />
    </header>

    <p
      v-if="loading"
      class="p-6 text-sm text-slate-400"
    >
      Loading workspace…
    </p>
    <div
      v-else-if="error || !workspace"
      class="flex flex-1 flex-col items-center justify-center gap-3 p-6 text-sm text-slate-500"
    >
      <p>{{ error ?? 'Workspace not found.' }}</p>
      <button
        type="button"
        class="rounded-md border border-slate-200 px-3 py-1 text-xs text-slate-600 hover:bg-slate-50"
        @click="goHome"
      >
        Back to workspaces
      </button>
    </div>

    <div v-else class="flex min-h-0 flex-1">
      <aside class="w-1/3 min-w-[280px] max-w-md border-r border-slate-200">
        <DocumentsPane :workspace-id="workspace.id" />
      </aside>
      <main class="flex-1">
        <ChatPane :workspace-id="workspace.id" :workspace-name="workspace.name" />
      </main>
    </div>
  </div>
</template>
