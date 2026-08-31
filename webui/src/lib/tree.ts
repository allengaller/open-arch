export interface Entry {
  name: string
  path: string
  isDir: boolean
  sizeBytes: number | null
}

export interface TreeNode {
  name: string
  path: string
  isDir: boolean
  sizeBytes: number | null
  children: TreeNode[]
}

export function buildTree(_rootName: string, entries: Entry[]): TreeNode[] {
  const root: TreeNode = { name: '', path: '', isDir: true, sizeBytes: null, children: [] }
  const findChild = (node: TreeNode, name: string) =>
    node.children.find((c) => c.name === name)

  for (const e of entries) {
    const parts = e.path.split('/')
    let cur = root
    for (let i = 0; i < parts.length - 1; i++) {
      const seg = parts[i]!
      let dir = findChild(cur, seg)
      if (!dir) {
        dir = {
          name: seg,
          path: parts.slice(0, i + 1).join('/'),
          isDir: true,
          sizeBytes: null,
          children: [],
        }
        cur.children.push(dir)
      }
      cur = dir
    }
    const name = parts[parts.length - 1]!
    if (findChild(cur, name)) continue
    cur.children.push({ name, path: e.path, isDir: e.isDir, sizeBytes: e.sizeBytes, children: [] })
  }

  const sortRec = (nodes: TreeNode[]) => {
    nodes.sort((a, b) =>
      a.isDir === b.isDir ? a.name.localeCompare(b.name) : a.isDir ? -1 : 1,
    )
    for (const n of nodes) sortRec(n.children)
  }
  sortRec(root.children)
  return root.children
}
