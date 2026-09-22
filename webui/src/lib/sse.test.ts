import { describe, expect, it } from 'vitest'
import { applyEvent, emptyChatState } from './sse'

describe('applyEvent', () => {
  it('REPLY_START 开启新气泡', () => {
    const s = applyEvent(emptyChatState(), { type: 'REPLY_START', reply_id: 'r1' })
    expect(s.bubbles).toHaveLength(1)
    expect(s.bubbles[0].replyId).toBe('r1')
    expect(s.bubbles[0].done).toBe(false)
  })

  it('TEXT_BLOCK_DELTA 拼接文本', () => {
    let s = emptyChatState()
    s = applyEvent(s, { type: 'REPLY_START', reply_id: 'r1' })
    s = applyEvent(s, { type: 'TEXT_BLOCK_DELTA', reply_id: 'r1', delta: '架构' })
    s = applyEvent(s, { type: 'TEXT_BLOCK_DELTA', reply_id: 'r1', delta: '方案' })
    expect(s.bubbles[0].text).toBe('架构方案')
  })

  it('多个 TEXT 块之间补空行', () => {
    let s = emptyChatState()
    s = applyEvent(s, { type: 'REPLY_START', reply_id: 'r1' })
    s = applyEvent(s, { type: 'TEXT_BLOCK_DELTA', reply_id: 'r1', block_id: 'b1', delta: 'A' })
    s = applyEvent(s, { type: 'TEXT_BLOCK_START', reply_id: 'r1', block_id: 'b2' })
    s = applyEvent(s, { type: 'TEXT_BLOCK_DELTA', reply_id: 'r1', block_id: 'b2', delta: 'B' })
    expect(s.bubbles[0].text).toBe('A\n\nB')
  })

  it('TOOL_CALL_START 建条目，TOOL_RESULT_TEXT_DELTA 拼结果', () => {
    let s = emptyChatState()
    s = applyEvent(s, { type: 'REPLY_START', reply_id: 'r1' })
    s = applyEvent(s, {
      type: 'TOOL_CALL_START', reply_id: 'r1',
      tool_call_id: 't1', tool_call_name: 'review_with_waf',
    })
    s = applyEvent(s, {
      type: 'TOOL_RESULT_TEXT_DELTA', reply_id: 'r1',
      tool_call_id: 't1', delta: '{"score":0.7}',
    })
    expect(s.bubbles[0].tools[0].name).toBe('review_with_waf')
    expect(s.bubbles[0].tools[0].resultText).toBe('{"score":0.7}')
  })

  it('REPLY_END 置 done', () => {
    let s = emptyChatState()
    s = applyEvent(s, { type: 'REPLY_START', reply_id: 'r1' })
    s = applyEvent(s, { type: 'REPLY_END', reply_id: 'r1' })
    expect(s.bubbles[0].done).toBe(true)
  })

  it('未知类型与缺 reply_id 的事件不抛错', () => {
    const s = applyEvent(emptyChatState(), { type: 'SOMETHING_NEW_IN_V3' })
    expect(s.bubbles).toHaveLength(0)
  })

  it('纯函数：不修改传入 state，相同输入产生相同输出', () => {
    // React setState updater 会被 StrictMode double-invoke；就地 mutate 会把
    // 流式 delta 拼两遍、且同引用返回触发 bail-out 不重渲染。
    const s0 = emptyChatState()
    const s1 = applyEvent(s0, { type: 'REPLY_START', reply_id: 'r1' })
    const ev = { type: 'TEXT_BLOCK_DELTA', reply_id: 'r1', delta: 'A' }
    const a = applyEvent(s1, ev)
    const b = applyEvent(s1, ev)
    expect(s0.bubbles).toHaveLength(0)
    expect(s1.bubbles[0].text).toBe('')
    expect(a).toEqual(b)
    expect(a).not.toBe(s1)
    expect(a.bubbles[0].text).toBe('A')
  })
})
