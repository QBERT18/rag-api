import {
  createChat as apiCreate,
  deleteChat as apiDelete,
  listChats as apiList,
  listMessages as apiListMessages,
  renameChat as apiRename,
  type Chat,
  type Citation,
  type StoredMessage,
} from '~/services/chat'

export interface UIMessage {
  role: 'user' | 'assistant'
  text: string
  sources?: Citation[]
}

const STORAGE_KEY = 'rag.activeChatId'
const DEFAULT_TITLE = 'New chat'

const chats = ref<Chat[]>([])
const activeChatId = ref<number | null>(null)
const messages = ref<UIMessage[]>([])
const loadingMessages = ref(false)

const inputHistoryByChat = new Map<number, string[]>()

function readStoredActiveId(): number | null {
  if (typeof window === 'undefined') return null
  const raw = window.localStorage.getItem(STORAGE_KEY)
  if (!raw) return null
  const n = Number.parseInt(raw, 10)
  return Number.isFinite(n) ? n : null
}

function writeStoredActiveId(id: number | null) {
  if (typeof window === 'undefined') return
  if (id === null) window.localStorage.removeItem(STORAGE_KEY)
  else window.localStorage.setItem(STORAGE_KEY, String(id))
}

function toUI(m: StoredMessage): UIMessage {
  return {
    role: m.role,
    text: m.content,
    sources: m.sources ?? undefined,
  }
}

async function refreshChats(): Promise<Chat[]> {
  chats.value = await apiList()
  return chats.value
}

async function hydrateMessages(chatId: number) {
  loadingMessages.value = true
  try {
    const rows = await apiListMessages(chatId)
    messages.value = rows.map(toUI)
  } finally {
    loadingMessages.value = false
  }
}

async function selectChat(id: number | null) {
  activeChatId.value = id
  writeStoredActiveId(id)
  if (id === null) {
    messages.value = []
    return
  }
  await hydrateMessages(id)
}

async function createChat(title?: string): Promise<Chat> {
  const chat = await apiCreate(title)
  chats.value = [chat, ...chats.value.filter((c) => c.id !== chat.id)]
  await selectChat(chat.id)
  return chat
}

async function renameChat(id: number, title: string): Promise<Chat> {
  const updated = await apiRename(id, title)
  const i = chats.value.findIndex((c) => c.id === id)
  if (i >= 0) chats.value[i] = updated
  return updated
}

async function deleteChat(id: number): Promise<void> {
  await apiDelete(id)
  chats.value = chats.value.filter((c) => c.id !== id)
  inputHistoryByChat.delete(id)
  if (activeChatId.value === id) {
    const next = chats.value[0]?.id ?? null
    await selectChat(next)
  }
}

async function init() {
  await refreshChats()
  const stored = readStoredActiveId()
  if (stored !== null && chats.value.some((c) => c.id === stored)) {
    await selectChat(stored)
  } else {
    activeChatId.value = null
    writeStoredActiveId(null)
  }
}

function appendLocal(msg: UIMessage) {
  messages.value.push(msg)
}

function patchLastAssistant(patch: Partial<UIMessage>) {
  for (let i = messages.value.length - 1; i >= 0; i--) {
    const m = messages.value[i]!
    if (m.role === 'assistant') {
      Object.assign(m, patch)
      break
    }
  }
}

function appendAssistantToken(token: string) {
  const last = messages.value[messages.value.length - 1]
  if (last && last.role === 'assistant') {
    last.text += token
  }
}

function setAssistantSources(sources: Citation[]) {
  const last = messages.value[messages.value.length - 1]
  if (last && last.role === 'assistant') {
    last.sources = sources
  }
}

function pushInputHistory(text: string) {
  const id = activeChatId.value
  if (id === null) return
  const arr = inputHistoryByChat.get(id) ?? []
  if (arr[arr.length - 1] !== text) arr.push(text)
  inputHistoryByChat.set(id, arr)
}

function getInputHistory(): string[] {
  const id = activeChatId.value
  if (id === null) return []
  return inputHistoryByChat.get(id) ?? []
}

function bumpChatToTop(id: number) {
  const idx = chats.value.findIndex((c) => c.id === id)
  if (idx > 0) {
    const [chat] = chats.value.splice(idx, 1)
    if (chat) chats.value.unshift(chat)
  }
}

export function useChats() {
  return {
    chats,
    activeChatId,
    messages,
    loadingMessages,
    init,
    refreshChats,
    selectChat,
    createChat,
    renameChat,
    deleteChat,
    appendLocal,
    patchLastAssistant,
    appendAssistantToken,
    setAssistantSources,
    pushInputHistory,
    getInputHistory,
    bumpChatToTop,
    DEFAULT_TITLE,
  }
}
