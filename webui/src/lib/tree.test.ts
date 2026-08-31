import { describe, expect, it } from 'vitest'
import { buildTree } from './tree'

describe('buildTree', () => {
  it('扁平 entries 构建嵌套树，目录在前文件按名排序', () => {
    const nodes = buildTree('工作区', [
      { name: 'a.md', path: 'a.md', isDir: false, sizeBytes: 1 },
      { name: 'deliverables', path: 'deliverables', isDir: true, sizeBytes: null },
      { name: 'x.md', path: 'deliverables/x.md', isDir: false, sizeBytes: 2 },
      { name: 'diagrams', path: 'diagrams', isDir: true, sizeBytes: null },
    ])
    expect(nodes.map((n) => n.name)).toEqual(['deliverables', 'diagrams', 'a.md'])
    expect(nodes[0].children[0].path).toBe('deliverables/x.md')
  })

  it('空 entries 返回空数组', () => {
    expect(buildTree('工作区', [])).toEqual([])
  })
})
