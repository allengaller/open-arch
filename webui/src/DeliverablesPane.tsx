import { useCallback, useEffect, useState } from 'react'
import type { AppCtx } from './App'
import { api } from './lib/api'
import { buildTree } from './lib/tree'
import type { Entry, TreeNode } from './lib/tree'
import { MarkdownView } from './MarkdownView'

interface Props {
  ctx: AppCtx
  sessionId: string | null
}

export function DeliverablesPane({ ctx, sessionId }: Props) {
  const [tree, setTree] = useState<TreeNode[]>([])
  const [preview, setPreview] = useState<{ name: string; text: string } | null>(null)

  // 递归列出工作区（深度上限 3 层），交付物目录通常只有两级
  const loadAll = useCallback(async () => {
    if (!sessionId) {
      setTree([])
      return
    }
    const entries: Entry[] = []
    const walk = async (path: string, depth: number): Promise<void> => {
      const listing = await api.listDirectory(ctx.agentId, sessionId, path)
      for (const e of listing.entries) {
        const childPath = path ? `${path}/${e.name}` : e.name
        entries.push({ name: e.name, path: childPath, isDir: e.is_dir, sizeBytes: e.size_bytes })
        if (e.is_dir && depth < 3) await walk(childPath, depth + 1)
      }
    }
    try {
      await walk('', 0)
      setTree(buildTree('工作区', entries))
    } catch {
      setTree([])
    }
  }, [ctx, sessionId])

  useEffect(() => {
    loadAll()
  }, [loadAll])

  const openFile = async (node: TreeNode) => {
    if (!sessionId) return
    if (node.name.endsWith('.drawio')) {
      window.open(api.downloadUrl(ctx.agentId, sessionId, node.path), '_blank')
      return
    }
    try {
      const text = await api.fileText(ctx.agentId, sessionId, node.path)
      setPreview({ name: node.name, text })
    } catch (e) {
      setPreview({ name: node.name, text: String(e) })
    }
  }

  return (
    <aside className="files">
      <div className="files-head">
        <span>交付物</span>
        <button className="btn btn-ghost" onClick={loadAll} title="刷新">
          ↻
        </button>
      </div>
      <Tree nodes={tree} onOpen={openFile} />
      {tree.length === 0 && <div className="empty-hint">暂无交付物</div>}
      {preview && (
        <div className="preview">
          <div className="preview-head">
            <span>{preview.name}</span>
            <button className="btn btn-ghost" onClick={() => setPreview(null)}>
              ×
            </button>
          </div>
          <MarkdownView role="assistant" text={preview.text} />
        </div>
      )}
    </aside>
  )
}

function Tree({
  nodes,
  onOpen,
  depth = 0,
}: {
  nodes: TreeNode[]
  onOpen: (n: TreeNode) => void
  depth?: number
}) {
  return (
    <ul className={depth === 0 ? 'file-tree' : 'file-tree nested'}>
      {nodes.map((n) => (
        <li key={n.path}>
          {n.isDir ? (
            <details open={depth < 1}>
              <summary>{n.name}/</summary>
              <Tree nodes={n.children} onOpen={onOpen} depth={depth + 1} />
            </details>
          ) : (
            <button className="file-link" onClick={() => onOpen(n)}>
              {n.name}
            </button>
          )}
        </li>
      ))}
    </ul>
  )
}
