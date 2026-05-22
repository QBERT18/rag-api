<script setup lang="ts">
const colorMode = useColorMode()

type Mode = 'system' | 'light' | 'dark'
const order: Mode[] = ['system', 'light', 'dark']

function cycle() {
  const current = (colorMode.preference as Mode) ?? 'system'
  const idx = order.indexOf(current)
  colorMode.preference = order[(idx + 1) % order.length]
}

const icon = computed(() => {
  switch (colorMode.preference) {
    case 'light':
      return 'lucide:sun'
    case 'dark':
      return 'lucide:moon'
    default:
      return 'lucide:monitor'
  }
})

const label = computed(() => {
  switch (colorMode.preference) {
    case 'light':
      return 'Light'
    case 'dark':
      return 'Dark'
    default:
      return 'System'
  }
})
</script>

<template>
  <button
    type="button"
    class="inline-flex items-center gap-1.5 rounded-md border border-border bg-surface px-2.5 py-1.5 text-xs text-muted transition hover:text-text hover:bg-surface-2"
    :title="`Theme: ${label}`"
    @click="cycle"
  >
    <Icon :name="icon" class="h-4 w-4" />
    <span class="hidden sm:inline">{{ label }}</span>
  </button>
</template>
