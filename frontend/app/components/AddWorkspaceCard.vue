<script setup lang="ts">
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
  const name = draft.value.trim()
  creating.value = false
  if (name) emit('create', name)
}

function cancel() {
  creating.value = false
  draft.value = ''
}
</script>

<template>
  <div
    class="flex aspect-[4/3] cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 p-5 text-slate-500 transition hover:border-slate-500 hover:bg-slate-100 hover:text-slate-700"
    @click="creating || start()"
  >
    <template v-if="!creating">
      <span class="text-4xl leading-none">+</span>
      <span class="mt-2 text-sm font-medium">New workspace</span>
    </template>
    <template v-else>
      <input
        ref="inputRef"
        v-model="draft"
        type="text"
        placeholder="Workspace name"
        class="w-full rounded border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
        @click.stop
        @keydown.enter.prevent="commit"
        @keydown.escape.prevent="cancel"
        @blur="commit"
      />
      <p class="mt-2 text-xs text-slate-400">Enter to create · Esc to cancel</p>
    </template>
  </div>
</template>
