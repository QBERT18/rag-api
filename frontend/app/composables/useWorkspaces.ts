import {
  createWorkspace as apiCreate,
  deleteWorkspace as apiDelete,
  listWorkspaces as apiList,
  renameWorkspace as apiRename,
  type Workspace,
} from '~/services/workspaces'

const workspaces = ref<Workspace[]>([])
const loaded = ref(false)

async function loadWorkspaces(): Promise<Workspace[]> {
  workspaces.value = await apiList()
  loaded.value = true
  return workspaces.value
}

async function createWorkspace(name: string): Promise<Workspace> {
  const ws = await apiCreate(name)
  workspaces.value = [ws, ...workspaces.value.filter((w) => w.id !== ws.id)]
  return ws
}

async function renameWorkspace(id: string, name: string): Promise<Workspace> {
  const updated = await apiRename(id, name)
  const i = workspaces.value.findIndex((w) => w.id === id)
  if (i >= 0) workspaces.value[i] = updated
  return updated
}

async function deleteWorkspace(id: string): Promise<void> {
  await apiDelete(id)
  workspaces.value = workspaces.value.filter((w) => w.id !== id)
}

function bumpToTop(id: string) {
  const i = workspaces.value.findIndex((w) => w.id === id)
  if (i > 0) {
    const [ws] = workspaces.value.splice(i, 1)
    if (ws) workspaces.value.unshift(ws)
  }
}

export function useWorkspaces() {
  return {
    workspaces,
    loaded,
    loadWorkspaces,
    createWorkspace,
    renameWorkspace,
    deleteWorkspace,
    bumpToTop,
  }
}
