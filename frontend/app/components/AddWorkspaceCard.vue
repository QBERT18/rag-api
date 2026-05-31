<script setup lang="ts">
defineProps<{ compact?: boolean }>()

const emit = defineEmits<{ (e: 'create', name: string): void }>()

const creating = ref(false)
const draft = ref('')
const inputRef = ref<HTMLInputElement | null>(null)

function start() {
  creating.value = true
  draft.value = ''
  nextTick(() => inputRef.value?.focus())
}

function commit() {
  if (!creating.value) return
  creating.value = false
  const name = draft.value.trim()
  if (name) emit('create', name)
}

function cancel() {
  creating.value = false
  draft.value = ''
}
</script>

<template>
  <div
    v-if="compact"
    class="flex cursor-pointer items-center gap-3 rounded-md border border-dashed border-border bg-surface px-3 py-2.5 text-muted transition hover:border-accent hover:text-text"
    @click="creating || start()"
  >
    <span
      class="flex h-9 w-9 items-center justify-center rounded-md bg-surface-2 text-muted"
    >
      <Icon name="lucide:plus" class="h-4 w-4" />
    </span>
    <template v-if="!creating">
      <p class="text-sm font-medium">New workspace</p>
    </template>
    <input
      v-else
      ref="inputRef"
      v-model="draft"
      type="text"
      placeholder="Workspace name"
      class="flex-1 rounded border border-border bg-bg px-2 py-1 text-sm text-text focus:border-accent focus:outline-none"
      @click.stop
      @keydown.enter.prevent="commit"
      @keydown.escape.prevent="cancel"
      @blur="commit"
    />
  </div>

  <div
    v-else
    class="flex aspect-[4/3] cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-border bg-surface p-5 text-muted transition hover:border-accent hover:bg-surface-2 hover:text-text"
    @click="creating || start()"
  >
    <template v-if="!creating">
      <span class="flex h-12 w-12 items-center justify-center rounded-full bg-surface-2">
        <Icon name="lucide:plus" class="h-6 w-6" />
      </span>
      <span class="mt-3 text-sm font-medium">New workspace</span>
    </template>
    <template v-else>
      <input
        ref="inputRef"
        v-model="draft"
        type="text"
        placeholder="Workspace name"
        class="w-full rounded border border-border bg-bg px-3 py-2 text-sm text-text focus:border-accent focus:outline-none"
        @click.stop
        @keydown.enter.prevent="commit"
        @keydown.escape.prevent="cancel"
        @blur="commit"
      />
      <p class="mt-2 text-xs text-muted">Enter to create · Esc to cancel</p>
    </template>
  </div>
</template>
