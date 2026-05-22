<script setup lang="ts">
import type { ViewMode } from '~/composables/useViewPreferences'

const props = defineProps<{ modelValue: ViewMode }>()
const emit = defineEmits<{ (e: 'update:modelValue', value: ViewMode): void }>()

function pick(mode: ViewMode) {
  if (mode !== props.modelValue) emit('update:modelValue', mode)
}
</script>

<template>
  <div
    class="inline-flex overflow-hidden rounded-md border border-border bg-surface"
    role="group"
  >
    <button
      type="button"
      class="flex items-center px-2.5 py-1.5 text-xs transition"
      :class="
        props.modelValue === 'grid'
          ? 'bg-surface-2 text-text'
          : 'text-muted hover:text-text'
      "
      title="Grid view"
      @click="pick('grid')"
    >
      <Icon name="lucide:layout-grid" class="h-4 w-4" />
    </button>
    <button
      type="button"
      class="flex items-center border-l border-border px-2.5 py-1.5 text-xs transition"
      :class="
        props.modelValue === 'list'
          ? 'bg-surface-2 text-text'
          : 'text-muted hover:text-text'
      "
      title="List view"
      @click="pick('list')"
    >
      <Icon name="lucide:list" class="h-4 w-4" />
    </button>
  </div>
</template>
