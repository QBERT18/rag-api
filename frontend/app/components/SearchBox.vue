<script setup lang="ts">
const props = defineProps<{
  modelValue: string
  placeholder?: string
}>()

const emit = defineEmits<{ (e: 'update:modelValue', value: string): void }>()

function onInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}

function clear() {
  emit('update:modelValue', '')
}
</script>

<template>
  <div class="relative flex items-center">
    <Icon
      name="lucide:search"
      class="pointer-events-none absolute left-2.5 h-4 w-4 text-muted"
    />
    <input
      type="text"
      :value="props.modelValue"
      :placeholder="props.placeholder ?? 'Search'"
      class="w-full rounded-md border border-border bg-surface py-1.5 pl-8 pr-8 text-sm text-text placeholder:text-muted focus:border-accent focus:outline-none"
      @input="onInput"
    />
    <button
      v-if="props.modelValue"
      type="button"
      class="absolute right-2 rounded p-0.5 text-muted hover:text-text"
      title="Clear"
      @click="clear"
    >
      <Icon name="lucide:x" class="h-3.5 w-3.5" />
    </button>
  </div>
</template>
