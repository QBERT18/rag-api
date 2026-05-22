<script setup lang="ts">
defineProps<{ tight?: boolean }>()
</script>

<template>
  <header
    class="border-b border-border bg-surface"
    :class="tight ? 'px-4 py-2' : 'px-6 py-4'"
  >
    <div class="mx-auto flex max-w-6xl items-center gap-3">
      <div class="flex min-w-0 flex-1 items-center gap-3">
        <slot name="left" />
      </div>
      <div class="flex items-center gap-2">
        <slot name="right" />
        <ThemeToggle />
      </div>
    </div>
  </header>
</template>
