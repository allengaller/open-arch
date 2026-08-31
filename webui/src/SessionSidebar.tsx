import type { SessionSummary } from './lib/api'

interface Props {
  sessions: SessionSummary[]
  currentId: string | null
  onSelect: (s: SessionSummary) => void
  onCreate: () => void
}

export function SessionSidebar({ sessions, currentId, onSelect, onCreate }: Props) {
  return (
    <aside className="sidebar">
      <div className="sidebar-head">
        <span className="brand">OpenArch</span>
        <button className="btn btn-primary" onClick={onCreate}>
          + 新会话
        </button>
      </div>
      <ul className="session-list">
        {sessions.map((s) => (
          <li key={s.id}>
            <button
              className={s.id === currentId ? 'session-item active' : 'session-item'}
              onClick={() => onSelect(s)}
            >
              <span className="session-name">{s.name}</span>
              {s.status === 'running' && <span className="dot" title="运行中" />}
            </button>
          </li>
        ))}
        {sessions.length === 0 && <li className="empty-hint">暂无会话</li>}
      </ul>
    </aside>
  )
}
