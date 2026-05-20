<script setup lang="ts">
const { chats, activeChatId, createChat, renameChat, deleteChat, selectChat } =
  useChats()

const error = ref<string | null>(null)

async function onNew() {
  error.value = null
  try {
    await createChat()
  } catch (e) {
    error.value = (e as Error).message
  }
}

async function onRename(id: number, title: string) {
  error.value = null
  try {
    await renameChat(id, title)
  } catch (e) {
    error.value = (e as Error).message
  }
}

async function onDelete(id: number) {
  error.value = null
  try {
    await deleteChat(id)
  } catch (e) {
    error.value = (e as Error).message
  }
}

async function onSelect(id: number) {
  if (activeChatId.value === id) return
  error.value = null
  try {
    await selectChat(id)
  } catch (e) {
    error.value = (e as Error).message
  }
}
</script>

<template>
  <div class="flex h-full flex-col">
    <header
      class="flex items-center justify-between border-b border-slate-200 p-4"
    >
      <h2 class="text-sm font-semibold text-slate-700">Chats</h2>
      <button
        type="button"
        class="rounded-md border border-slate-200 px-2 py-1 text-xs text-slate-600 hover:bg-slate-50"
        @click="onNew"
      >
        + New
      </button>
    </header>

    <p v-if="error" class="px-4 pt-2 text-xs text-red-600">{{ error }}</p>

    <ul v-if="chats.length" class="flex-1 overflow-y-auto py-1">
      <ChatListItem
        v-for="chat in chats"
        :key="chat.id"
        :chat="chat"
        :active="chat.id === activeChatId"
        @select="onSelect"
        @rename="onRename"
        @delete="onDelete"
      />
    </ul>
    <p v-else class="p-4 text-sm text-slate-400">
      No chats yet. Click <span class="font-medium">+ New</span> to start one.
    </p>
  </div>
</template>
