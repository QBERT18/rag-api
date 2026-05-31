<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    open: boolean
    title?: string
    message?: string
    confirmLabel?: string
    cancelLabel?: string
    tone?: 'danger' | 'default'
  }>(),
  {
    title: 'Are you sure?',
    message: '',
    confirmLabel: 'Delete',
    cancelLabel: 'Cancel',
    tone: 'danger',
  },
)

const emit = defineEmits<{ (e: 'confirm'): void; (e: 'cancel'): void }>()

const confirmRef = ref<HTMLButtonElement | null>(null)

watch(
  () => props.open,
  (open) => {
    if (open) nextTick(() => confirmRef.value?.focus())
  },
)
</script>

<template>
  <Teleport to="body">
    <Transition name="confirm">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
        @click="emit('cancel')"
        @keydown.escape.prevent="emit('cancel')"
      >
        <div
          class="confirm-panel w-full max-w-sm rounded-lg border border-border bg-bg p-5 shadow-lg"
          role="dialog"
          aria-modal="true"
          aria-labelledby="confirm-title"
          @click.stop
        >
          <h2 id="confirm-title" class="text-base font-semibold text-text">
            {{ title }}
          </h2>
          <p v-if="message" class="mt-2 text-sm text-muted">
            {{ message }}
          </p>

          <div class="mt-5 flex justify-end gap-2">
            <button
              type="button"
              class="rounded-md border border-border bg-surface px-3 py-1.5 text-sm text-muted transition hover:bg-surface-2 hover:text-text"
              @click="emit('cancel')"
            >
              {{ cancelLabel }}
            </button>
            <button
              ref="confirmRef"
              type="button"
              class="rounded-md px-3 py-1.5 text-sm transition hover:opacity-90"
              :class="
                tone === 'danger'
                  ? 'bg-danger text-white'
                  : 'bg-accent text-accent-fg'
              "
              @click="emit('confirm')"
            >
              {{ confirmLabel }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.confirm-enter-active,
.confirm-leave-active {
  transition: opacity 160ms ease-out;
}
.confirm-enter-from,
.confirm-leave-to {
  opacity: 0;
}
.confirm-enter-active .confirm-panel,
.confirm-leave-active .confirm-panel {
  transition: transform 160ms ease-out;
}
.confirm-enter-from .confirm-panel,
.confirm-leave-to .confirm-panel {
  transform: scale(0.95);
}
</style>
