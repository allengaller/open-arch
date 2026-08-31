export interface ToolEntry {
  toolCallId: string
  name: string
  resultText: string
  done: boolean
}

export interface Bubble {
  replyId: string
  text: string
  thinking: string
  tools: ToolEntry[]
  done: boolean
}

export interface ChatStreamState {
  bubbles: Bubble[]
}

export function emptyChatState(): ChatStreamState {
  return { bubbles: [] }
}

function upsertBubble(state: ChatStreamState, replyId: string): Bubble {
  let b = state.bubbles.find((x) => x.replyId === replyId)
  if (!b) {
    b = { replyId, text: '', thinking: '', tools: [], done: false }
    state.bubbles.push(b)
  }
  return b
}

function upsertTool(bubble: Bubble, toolCallId: string, name?: string): ToolEntry {
  let t = bubble.tools.find((x) => x.toolCallId === toolCallId)
  if (!t) {
    t = { toolCallId, name: name ?? '', resultText: '', done: false }
    bubble.tools.push(t)
  } else if (name) {
    t.name = name
  }
  return t
}

// 宽容解析：未知 type 一律忽略——AgentScope 升级新增事件类型时前端不炸。
export function applyEvent(
  state: ChatStreamState,
  ev: Record<string, unknown>,
): ChatStreamState {
  const type = ev['type'] as string | undefined
  const replyId = (ev['reply_id'] as string | undefined) ?? 'unknown'
  switch (type) {
    case 'REPLY_START':
      upsertBubble(state, replyId)
      break
    case 'TEXT_BLOCK_START': {
      const b = upsertBubble(state, replyId)
      if (b.text !== '') b.text += '\n\n'
      break
    }
    case 'TEXT_BLOCK_DELTA': {
      const b = upsertBubble(state, replyId)
      b.text += (ev['delta'] as string | undefined) ?? ''
      break
    }
    case 'THINKING_BLOCK_DELTA': {
      const b = upsertBubble(state, replyId)
      b.thinking += (ev['delta'] as string | undefined) ?? ''
      break
    }
    case 'TOOL_CALL_START': {
      const b = upsertBubble(state, replyId)
      upsertTool(
        b,
        (ev['tool_call_id'] as string | undefined) ?? '',
        ev['tool_call_name'] as string | undefined,
      )
      break
    }
    case 'TOOL_RESULT_TEXT_DELTA': {
      const b = upsertBubble(state, replyId)
      const t = upsertTool(b, (ev['tool_call_id'] as string | undefined) ?? '')
      t.resultText += (ev['delta'] as string | undefined) ?? ''
      break
    }
    case 'TOOL_CALL_END':
    case 'TOOL_RESULT_END': {
      const b = upsertBubble(state, replyId)
      const t = upsertTool(b, (ev['tool_call_id'] as string | undefined) ?? '')
      t.done = true
      break
    }
    case 'REPLY_END': {
      const b = upsertBubble(state, replyId)
      b.done = true
      break
    }
    default:
      // 心跳注释帧、未知类型：忽略
      break
  }
  return state
}

// ---- 传输层（fetch 式 SSE：EventSource 无法带 X-User-ID 头）----

function parseSseData(frame: string): string[] {
  const out: string[] = []
  let cur = ''
  for (const line of frame.split('\n')) {
    if (line.startsWith('data:')) {
      cur += (cur ? '\n' : '') + line.slice(5).trimStart()
    }
  }
  if (cur) out.push(cur)
  return out
}

export interface StreamCallbacks {
  onEvent: (ev: Record<string, unknown>) => void
  onClose?: (err?: unknown) => void
}

export async function streamSessionEvents(
  agentId: string,
  sessionId: string,
  cb: StreamCallbacks,
  signal?: AbortSignal,
): Promise<void> {
  const url = `/sessions/${encodeURIComponent(sessionId)}/stream?agent_id=${encodeURIComponent(agentId)}`
  try {
    const resp = await fetch(url, {
      headers: { 'X-User-ID': 'local', Accept: 'text/event-stream' },
      signal,
    })
    if (!resp.ok || !resp.body) throw new Error(`SSE 连接失败：HTTP ${resp.status}`)
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buf = ''
    for (;;) {
      const { done, value } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })
      let idx: number
      while ((idx = buf.indexOf('\n\n')) >= 0) {
        const frame = buf.slice(0, idx)
        buf = buf.slice(idx + 2)
        for (const data of parseSseData(frame)) {
          try {
            cb.onEvent(JSON.parse(data) as Record<string, unknown>)
          } catch {
            // 非 JSON 的 data 行忽略
          }
        }
      }
    }
    cb.onClose?.()
  } catch (err) {
    if (!signal?.aborted) cb.onClose?.(err)
  }
}
