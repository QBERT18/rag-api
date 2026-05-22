import DOMPurify from 'dompurify'
import hljs from 'highlight.js/lib/common'
import { Marked } from 'marked'
import { markedHighlight } from 'marked-highlight'

const marked = new Marked(
  markedHighlight({
    emptyLangClass: 'hljs',
    langPrefix: 'hljs language-',
    highlight(code, lang) {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return hljs.highlight(code, { language: lang, ignoreIllegals: true }).value
        } catch {
          return code
        }
      }
      try {
        return hljs.highlightAuto(code).value
      } catch {
        return code
      }
    },
  }),
)

marked.setOptions({ gfm: true, breaks: true })

let hookInstalled = false

function ensureHook() {
  if (hookInstalled) return
  if (typeof window === 'undefined') return
  DOMPurify.addHook('afterSanitizeAttributes', (node) => {
    if ((node as Element).tagName === 'A') {
      const el = node as HTMLAnchorElement
      el.setAttribute('target', '_blank')
      el.setAttribute('rel', 'noopener noreferrer')
    }
  })
  hookInstalled = true
}

export function renderMarkdown(raw: string): string {
  if (!import.meta.client) return ''
  ensureHook()
  const html = marked.parse(raw) as string
  return DOMPurify.sanitize(html, { ADD_ATTR: ['target', 'rel'] })
}
