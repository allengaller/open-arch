import { useCallback, useEffect, useState } from 'react'
import { api } from './lib/api'
import type { SkillPack } from './lib/api'
import { fileLabel } from './lib/knowledge'
import { MarkdownView } from './MarkdownView'

// 知识库视图：浏览 skills/ 技能包的 Markdown 知识正文（/openarch/skills 只读端点）。
// notice：无后端（演示模式）时的友好提示，替代原始报错。
interface Selected {
  pack: string
  path: string
}

export function KnowledgePane({ notice }: { notice?: string }) {
  const [packs, setPacks] = useState<SkillPack[]>([])
  const [selected, setSelected] = useState<Selected | null>(null)
  const [text, setText] = useState('')
  const [error, setError] = useState('')

  const loadFile = useCallback(async (pack: string, path: string) => {
    setSelected({ pack, path })
    setText('')
    setError('')
    try {
      setText(await api.skillText(pack, path))
    } catch (e) {
      setError(String(e))
    }
  }, [])

  useEffect(() => {
    ;(async () => {
      try {
        const { skills } = await api.listSkills()
        setPacks(skills)
        // 默认展开第一个技能包的第一篇正文，跳过 SKILL.md 说明页
        const first = skills[0]
        if (first) {
          const file = first.files.find((f) => f !== 'SKILL.md') ?? first.files[0]
          if (file) await loadFile(first.name, file)
        }
      } catch (e) {
        setError(String(e))
      }
    })()
  }, [loadFile])

  return (
    <main className="knowledge">
      <nav className="k-nav" aria-label="知识库导航">
        {packs.map((p) => (
          <div className="k-pack" key={p.name}>
            <div className="k-pack-name">{p.name}</div>
            <div className="k-pack-desc">{p.description}</div>
            {p.files.map((f) => (
              <button
                key={f}
                className={
                  selected && selected.pack === p.name && selected.path === f
                    ? 'k-file active'
                    : 'k-file'
                }
                onClick={() => loadFile(p.name, f)}
                title={f}
              >
                {fileLabel(f)}
              </button>
            ))}
          </div>
        ))}
        {packs.length === 0 && !error && <div className="empty-hint">暂无技能包</div>}
      </nav>
      <div className="k-main">
        {error ? <div className="k-error">{notice ?? error}</div> : null}
        {!error && !text && <div className="k-loading">加载中…</div>}
        {text ? <MarkdownView role="assistant" text={text} /> : null}
      </div>
    </main>
  )
}
