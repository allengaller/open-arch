import DOMPurify from 'dompurify'
import { marked } from 'marked'
import { useEffect, useState } from 'react'
import { renderMermaid, splitMermaidSegments } from './lib/mermaid'

export function MarkdownView({
  role,
  text,
  live,
}: {
  role: string
  text: string
  live?: boolean
}) {
  const segments = splitMermaidSegments(text)
  return (
    <div className={`msg ${role === 'user' ? 'user' : 'assistant'}`}>
      {segments.map((seg, i) =>
        seg.kind === 'text' ? (
          <div
            key={i}
            className="md"
            dangerouslySetInnerHTML={{
              __html: DOMPurify.sanitize(marked.parse(seg.content, { async: false }) as string),
            }}
          />
        ) : (
          <MermaidBlock key={i} code={seg.content} live={live} />
        ),
      )}
    </div>
  )
}

function MermaidBlock({ code, live }: { code: string; live?: boolean }) {
  const [svg, setSvg] = useState<string | null>(null)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    if (live) return
    let cancelled = false
    renderMermaid(code)
      .then((s) => {
        if (!cancelled) {
          setSvg(s)
          setFailed(false)
        }
      })
      .catch(() => {
        if (!cancelled) setFailed(true)
      })
    return () => {
      cancelled = true
    }
  }, [code, live])

  if (live) return <pre className="code">{code}</pre>
  if (failed) return <pre className="code">{code}</pre>
  if (!svg) return <div className="mermaid-loading">渲染图中…</div>
  return <div className="mermaid" dangerouslySetInnerHTML={{ __html: svg }} />
}
