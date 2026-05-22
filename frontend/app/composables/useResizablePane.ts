interface Options {
  storageKey: string
  initial: number
  min: number
  minOther: number
}

export function useResizablePane(opts: Options) {
  const width = ref(opts.initial)
  const dragging = ref(false)
  const containerRef = ref<HTMLElement | null>(null)

  function clamp(value: number): number {
    const container = containerRef.value
    const containerWidth = container?.clientWidth ?? window.innerWidth
    const max = Math.max(opts.min, containerWidth - opts.minOther)
    return Math.min(Math.max(value, opts.min), max)
  }

  function onPointerMove(event: PointerEvent) {
    if (!dragging.value) return
    const container = containerRef.value
    if (!container) return
    const left = container.getBoundingClientRect().left
    width.value = clamp(event.clientX - left)
  }

  function endDrag() {
    if (!dragging.value) return
    dragging.value = false
    document.body.style.userSelect = ''
    document.body.style.cursor = ''
    window.removeEventListener('pointermove', onPointerMove)
    window.removeEventListener('pointerup', endDrag)
    window.localStorage.setItem(opts.storageKey, String(width.value))
  }

  function startDrag(event: PointerEvent) {
    event.preventDefault()
    dragging.value = true
    document.body.style.userSelect = 'none'
    document.body.style.cursor = 'col-resize'
    window.addEventListener('pointermove', onPointerMove)
    window.addEventListener('pointerup', endDrag)
  }

  function onWindowResize() {
    width.value = clamp(width.value)
  }

  onMounted(() => {
    const stored = window.localStorage.getItem(opts.storageKey)
    if (stored) {
      const parsed = Number(stored)
      if (Number.isFinite(parsed)) width.value = clamp(parsed)
    } else {
      width.value = clamp(width.value)
    }
    window.addEventListener('resize', onWindowResize)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', onWindowResize)
    window.removeEventListener('pointermove', onPointerMove)
    window.removeEventListener('pointerup', endDrag)
  })

  return { width, dragging, containerRef, startDrag }
}
