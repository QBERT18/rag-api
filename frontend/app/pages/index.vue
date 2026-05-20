<script setup lang="ts">
const router = useRouter()
const {
  workspaces,
  loadWorkspaces,
  createWorkspace,
  renameWorkspace,
  deleteWorkspace,
} = useWorkspaces()

const error = ref<string | null>(null)

onMounted(async () => {
  try {
    await loadWorkspaces()
  } catch (e) {
    error.value = (e as Error).message
  }
})

async function onCreate(name: string) {
  error.value = null
  try {
    const ws = await createWorkspace(name)
    router.push(`/workspaces/${ws.id}`)
  } catch (e) {
    error.value = (e as Error).message
  }
}

function onOpen(id: string) {
  router.push(`/workspaces/${id}`)
}

async function onRename(id: string, name: string) {
  error.value = null
  try {
    await renameWorkspace(id, name)
  } catch (e) {
    error.value = (e as Error).message
  }
}

async function onDelete(id: string) {
  error.value = null
  try {
    await deleteWorkspace(id)
  } catch (e) {
    error.value = (e as Error).message
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <header class="border-b border-slate-200 bg-white">
      <div class="mx-auto max-w-6xl px-6 py-5">
        <h1 class="text-xl font-semibold text-slate-900">Workspaces</h1>
        <p class="mt-1 text-sm text-slate-500">
          Each workspace has its own files and chat history.
        </p>
      </div>
    </header>

    <main class="mx-auto max-w-6xl px-6 py-8">
      <p v-if="error" class="mb-4 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
        {{ error }}
      </p>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <WorkspaceCard
          v-for="ws in workspaces"
          :key="ws.id"
          :workspace="ws"
          @open="onOpen"
          @rename="onRename"
          @delete="onDelete"
        />
        <AddWorkspaceCard @create="onCreate" />
      </div>
    </main>
  </div>
</template>
