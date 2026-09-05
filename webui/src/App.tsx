import { useCallback, useEffect, useState } from 'react'
import { ChatPane } from './ChatPane'
import { DemoConsole } from './DemoConsole'
import { DeliverablesPane } from './DeliverablesPane'
import { KnowledgePane } from './KnowledgePane'
import { api } from './lib/api'
import { isBootFailure } from './lib/demo'
import type { SessionSummary } from './lib/api'
import { SessionSidebar } from './SessionSidebar'

export interface AppCtx {
  agentId: string
  credentialId: string
  model: string
}

type View = 'console' | 'knowledge'

export default function App() {
  const [ctx, setCtx] = useState<AppCtx | null>(null)
  const [sessions, setSessions] = useState<SessionSummary[]>([])
  const [current, setCurrent] = useState<SessionSummary | null>(null)
  const [error, setError] = useState('')
  const [demo, setDemo] = useState(false)
  const [ready, setReady] = useState(false)
  const [view, setView] = useState<View>('console')

  useEffect(() => {
    ;(async () => {
      try {
        const cfg = await api.config()
        const [agentId, credentialId] = await Promise.all([api.agentId(), api.credentialId()])
        setCtx({ agentId, credentialId, model: cfg.model })
        const s = await api.listSessions(agentId)
        setSessions(
          s.sessions.map((v) => ({
            id: v.session.id,
            name: v.session.config.name,
            status: v.status,
          })),
        )
        setReady(true)
      } catch (e) {
        if (isBootFailure(e)) {
          setDemo(true)
          setReady(true)
        } else {
          setError(String(e))
        }
      }
    })()
  }, [])

  const refreshSessions = useCallback(async () => {
    if (!ctx) return
    const s = await api.listSessions(ctx.agentId)
    setSessions(
      s.sessions.map((v) => ({
        id: v.session.id,
        name: v.session.config.name,
        status: v.status,
      })),
    )
  }, [ctx])

  const createSession = useCallback(async () => {
    if (!ctx) return
    try {
      const { session_id } = await api.createSession(ctx.agentId, ctx.credentialId, ctx.model)
      await refreshSessions()
      setCurrent({ id: session_id, name: '新会话', status: 'idle' })
    } catch (e) {
      setError(String(e))
    }
  }, [ctx, refreshSessions])

  if (error) return <div className="boot boot-error">启动失败：{error}</div>
  if (demo) return <DemoConsole />
  if (!ready) return <div className="boot">加载中…</div>
  return (
    <div className="app">
      <header className="appbar">
        <span className="brand">
          <span className="brand-mark">O</span>
          OpenArch<small>控制台</small>
        </span>
        <nav className="view-tabs" aria-label="视图切换">
          <button
            className={view === 'console' ? 'view-tab active' : 'view-tab'}
            onClick={() => setView('console')}
          >
            控制台
          </button>
          <button
            className={view === 'knowledge' ? 'view-tab active' : 'view-tab'}
            onClick={() => setView('knowledge')}
          >
            知识库
          </button>
        </nav>
        <span className="appbar-spacer" />
        <a className="gtm-link" href="/gtm/index.html" rel="noopener">返回项目主页 →</a>
      </header>
      {view === 'knowledge' ? (
        <KnowledgePane />
      ) : (
        <>
          <SessionSidebar
            sessions={sessions}
            currentId={current?.id ?? null}
            onSelect={setCurrent}
            onCreate={createSession}
          />
          <ChatPane ctx={ctx!} session={current} onSessionsChanged={refreshSessions} />
          <DeliverablesPane ctx={ctx!} sessionId={current?.id ?? null} />
        </>
      )}
    </div>
  )
}