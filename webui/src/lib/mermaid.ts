export interface Segment {
  kind: 'text' | 'mermaid'
  content: string
}

const FENCE = /^```mermaid[ \t]*\r?\n([\s\S]*?)^```[ \t]*$/gm

export function splitMermaidSegments(text: string): Segment[] {
  const segments: Segment[] = []
  let last = 0
  FENCE.lastIndex = 0
  for (const m of text.matchAll(FENCE)) {
    const start = m.index ?? 0
    if (start > last) segments.push({ kind: 'text', content: text.slice(last, start) })
    segments.push({ kind: 'mermaid', content: m[1].trim() })
    last = start + m[0].length
  }
  if (last < text.length) segments.push({ kind: 'text', content: text.slice(last) })
  return segments
}

let mermaidReady: Promise<typeof import('mermaid').default> | null = null

function loadMermaid() {
  if (!mermaidReady) {
    mermaidReady = import('mermaid').then((m) => {
      m.default.initialize({ startOnLoad: false, securityLevel: 'strict' })
      return m.default
    })
  }
  return mermaidReady
}

export async function renderMermaid(code: string): Promise<string> {
  const mermaid = await loadMermaid()
  const { svg } = await mermaid.render(
    `mmd-${Math.random().toString(36).slice(2)}`,
    code,
  )
  return svg
}
