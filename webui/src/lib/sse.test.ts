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
})
