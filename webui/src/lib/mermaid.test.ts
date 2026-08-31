import { describe, expect, it } from 'vitest'
import { splitMermaidSegments } from './mermaid'

describe('splitMermaidSegments', () => {
  it('提取单个 mermaid 块，前后文保留', () => {
    const segs = splitMermaidSegments('前文\n```mermaid\nflowchart LR\n  a-->b\n```\n后文')
    expect(segs).toEqual([
      { kind: 'text', content: '前文\n' },
      { kind: 'mermaid', content: 'flowchart LR\n  a-->b' },
      { kind: 'text', content: '\n后文' },
    ])
  })

  it('无块时整体为 text', () => {
    expect(splitMermaidSegments('纯文本')).toEqual([{ kind: 'text', content: '纯文本' }])
  })

  it('多个块全部提取', () => {
    const segs = splitMermaidSegments('```mermaid\na-->b\n```\n中\n```mermaid\nc-->d\n```')
    expect(segs.filter((s) => s.kind === 'mermaid')).toHaveLength(2)
  })
})
