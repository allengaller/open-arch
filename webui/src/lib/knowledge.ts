// 知识库导航标签：把技能包内文件路径转成侧栏短标签。
export function fileLabel(path: string): string {
  if (path === 'SKILL.md') return '说明 · SKILL.md'
  const base = path.startsWith('content/') ? path.slice('content/'.length) : path
  return base.replace(/\.(md|yaml|yml)$/, '')
}
