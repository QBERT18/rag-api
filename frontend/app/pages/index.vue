<script setup lang="ts">
import type { SortKey } from '~/composables/useViewPreferences'

const router = useRouter()
const {
  workspaces,
  loadWorkspaces,
  createWorkspace,
  renameWorkspace,
  deleteWorkspace,
} = useWorkspaces()

const { viewMode, sortKey } = useViewPreferences()

const error = ref<string | null>(null)
const query = ref('')

onMounted(async () => {
  try {
    await loadWorkspaces()
  } catch (e) {
    error.value = (e as Error).message
  }
})

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  const base = q
    ? workspaces.value.filter((w) => w.name.toLowerCase().includes(q))
    : [...workspaces.value]

  const sorted = base.slice()
  switch (sortKey.value) {
    case 'title':
      sorted.sort((a, b) => a.name.localeCompare(b.name))
      break
    case 'created':
      sorted.sort((a, b) => b.created_at.localeCompare(a.created_at))
      break
    default:
      sorted.sort((a, b) => b.updated_at.localeCompare(a.updated_at))
  }
  return sorted
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

function setSort(key: SortKey) {
  sortKey.value = key
}
</script>

<template>
  <div class="min-h-screen bg-bg text-text">
    <AppHeader>
      <template #left>
        <h1 class="text-lg font-semibold text-text">Workspaces</h1>
      </template>
    </AppHeader>

    <main class="mx-auto max-w-6xl px-6 py-6">
      <div class="mb-6 flex flex-wrap items-center gap-3">
        <div class="min-w-0 flex-1">
          <SearchBox v-model="query" placeholder="Search workspaces" />
        </div>
        <div class="relative">
          <select
            :value="sortKey"
            class="appearance-none rounded-md border border-border bg-surface py-1.5 pl-3 pr-9 text-sm text-text focus:border-accent focus:outline-none"
            @change="setSort(($event.target as HTMLSelectElement).value as SortKey)"
          >
            <option value="updated">Recently updated</option>
            <option value="title">Title A→Z</option>
            <option value="created">Date created</option>
          </select>
          <Icon
            name="lucide:chevron-down"
            class="pointer-events-none absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted"
          />
        </div>
        <ViewToggle v-model="viewMode" />
      </div>

      <p
        v-if="error"
        class="mb-4 rounded border border-danger/40 bg-[var(--color-danger-soft)] px-3 py-2 text-sm text-danger"
      >
        {{ error }}
      </p>

      <template v-if="viewMode === 'grid'">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <AddWorkspaceCard @create="onCreate" />
          <WorkspaceCard
            v-for="ws in filtered"
            :key="ws.id"
            :workspace="ws"
            @open="onOpen"
            @rename="onRename"
            @delete="onDelete"
          />
        </div>
        <p
          v-if="!filtered.length && query"
          class="mt-6 text-sm text-muted"
        >
          No workspaces match “{{ query }}”.
        </p>
      </template>

      <template v-else>
        <div class="flex flex-col gap-2">
          <AddWorkspaceCard compact @create="onCreate" />
          <WorkspaceListRow
            v-for="ws in filtered"
            :key="ws.id"
            :workspace="ws"
            @open="onOpen"
            @rename="onRename"
            @delete="onDelete"
          />
          <p
            v-if="!filtered.length && query"
            class="mt-2 text-sm text-muted"
          >
            No workspaces match “{{ query }}”.
          </p>
        </div>
      </template>
    </main>
  </div>
</template>
