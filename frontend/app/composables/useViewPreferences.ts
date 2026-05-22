export type ViewMode = 'grid' | 'list'
export type SortKey = 'updated' | 'title' | 'created'

const STORAGE_KEY = 'rag-view-prefs'

interface Prefs {
  viewMode: ViewMode
  sortKey: SortKey
}

const DEFAULTS: Prefs = { viewMode: 'grid', sortKey: 'updated' }

function readStored(): Prefs {
  if (typeof window === 'undefined') return DEFAULTS
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return DEFAULTS
    const parsed = JSON.parse(raw) as Partial<Prefs>
    return {
      viewMode: parsed.viewMode === 'list' ? 'list' : 'grid',
      sortKey:
        parsed.sortKey === 'title' || parsed.sortKey === 'created'
          ? parsed.sortKey
          : 'updated',
    }
  } catch {
    return DEFAULTS
  }
}

export function useViewPreferences() {
  const viewMode = useState<ViewMode>('view-mode', () => DEFAULTS.viewMode)
  const sortKey = useState<SortKey>('sort-key', () => DEFAULTS.sortKey)

  onMounted(() => {
    const stored = readStored()
    viewMode.value = stored.viewMode
    sortKey.value = stored.sortKey
  })

  function persist() {
    if (typeof window === 'undefined') return
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ viewMode: viewMode.value, sortKey: sortKey.value }),
    )
  }

  watch([viewMode, sortKey], persist)

  return { viewMode, sortKey }
}
