import { useCallback, useEffect, useRef, useState } from 'react'
import type { AppCtx } from './App'
import type { SessionSummary } from './lib/api'
import { api } from './lib/api'
import type { Bubble } from './lib/sse'
import { applyEvent, streamSessionEvents } from './lib/sse'
import { MarkdownView } from './MarkdownView'

interface Props {
  ctx: AppCtx
  session: SessionSummary | null
  onSessionsChanged: () => void
}

interface HistoryMsg {
  role: string
  content: { type: string; text?: string }[]
}

export function ChatPane({ ctx, session, onSessionsChanged }: Props) {
  const [history, setHistory] = useState<HistoryMsg[]>([])
  const [live, setLive] = useState<Bubble[]>([])
  const [input, setInput] = useState('')
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  // 选中会话：载历史 + 订阅事件流（断线 1.5s 后重连，服务端会先回放缓冲）
  useEffect(() => {
    if (!session) return
    let cancelled = false
    let retryTimer: ReturnType<typeof setTimeout> | undefined
    setHistory([])
    setLive([])
    setError('')
    setRunning(false)
    ;(async () => {
      try {
        const m = await api.listMessages(ctx.agentId, session.id)
        if (!cancelled) setHistory(m.messages as HistoryMsg[])
      } catch (e) {
        if (!cancelled) setError(String(e))
      }
    })()
    const ctrl = new AbortController()
    const pump = () => {
      streamSessionEvents(
        ctx.agentId,
        session.id,
        {
          onEvent: (ev) => {
            if (cancelled) return
            setLive((prev) => applyEvent({ bubbles: prev }, ev).bubbles)
            const t = ev['type']
            if (t === 'REPLY_START') setRunning(true)
            if (t === 'REPLY_END' || t === 'USER_INTERRUPT') {
              setRunning(false)
              onSessionsChanged()
            }
          },
          onClose: () => {
            if (!cancelled && !ctrl.signal.aborted) retryTimer = setTimeout(pump, 1500)
          },
        },
        ctrl.signal,
      )
    }
    pump()
    return () => {
      cancelled = true
      if (retryTimer) clearTimeout(retryTimer)
      ctrl.abort()
    }
  }, [session?.id, ctx, onSessionsChanged])

  // 全部 live 气泡完成后对账：以服务端持久化历史为准，清空实时态
  useEffect(() => {
    if (!session || live.length === 0 || !live.every((b) => b.done)) return
    let cancelled = false
    ;(async () => {
      try {
        const m = await api.listMessages(ctx.agentId, session.id)
        if (!cancelled) {
          setHistory(m.messages as HistoryMsg[])
          setLive([])
        }
      } catch {
        // 对账失败保留 live 内容
      }
    })()
    return () => {
      cancelled = true
    }
  }, [live, session, ctx])

  const send = useCallback(async () => {
    if (!session || !input.trim() || running) return
    const text = input.trim()
    setInput('')
    setHistory((prev) => [
      ...prev,
      { role: 'user', content: [{ type: 'text', text }] },
    ])
    setRunning(true)
    try {
      await api.chat(ctx.agentId, session.id, text)
    } catch (e) {
      setError(String(e))
      setRunning(false)
    }
  }, [session, input, running, ctx])

  const interrupt = useCallback(async () => {
    if (!session) return
    try {
      await api.interrupt(ctx.agentId, session.id)
    } catch (e) {
      setError(String(e))
    }
  }, [session, ctx])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history, live])

  if (!session) {
    return (
      <main className="chat chat-empty">
        <p>从左侧选择一个会话，或点击「+ 新会话」开始。</p>
        <p className="muted">
          工作流：需求澄清 → 方案生成 → Mermaid 架构图 → WAF 评审 → 交付文档
        </p>
      </main>
    )
  }

  return (
    <main className="chat">
      <div className="chat-scroll">
        {history.map((m, i) => (
          <MarkdownView
            key={i}
            role={m.role}
            text={(m.content ?? [])
              .filter((c) => c.type === 'text')
              .map((c) => c.text ?? '')
              .join('\n')}
          />
        ))}
        {live.map((b) => (
          <LiveBubble key={b.replyId} bubble={b} />
        ))}
        <div ref={bottomRef} />
      </div>
      {error && (
        <div className="chat-error" onClick={() => setError('')}>
          {error}（点击关闭）
        </div>
      )}
      <div className="chat-input">
        <textarea
          value={input}
          placeholder={
            running
              ? '回复进行中…'
              : '描述你的业务需求，例如：为一个日均 10 万单的电商系统设计高可用架构'
          }
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              send()
            }
          }}
        />
        {running ? (
          <button className="btn btn-danger" onClick={interrupt}>
            中断
          </button>
        ) : (
          <button className="btn btn-primary" onClick={send} disabled={!input.trim()}>
            发送
          </button>
        )}
      </div>
    </main>
  )
}

function LiveBubble({ bubble }: { bubble: Bubble }) {
  return (
    <div className="msg assistant streaming">
      {bubble.thinking && (
        <details className="thinking">
          <summary>思考过程</summary>
          <pre>{bubble.thinking}</pre>
        </details>
      )}
      {bubble.tools.map((t) => (
        <details key={t.toolCallId} className="tool-entry">
          <summary>
            {t.done ? '🔧' : '⏳'} {t.name || '工具调用'}
          </summary>
          <pre className="tool-result">{t.resultText}</pre>
        </details>
      ))}
      <MarkdownView role="assistant" text={bubble.text} live={!bubble.done} />
    </div>
  )
}
