import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it, vi } from 'vitest'

// node 测试环境无 DOM，DOMPurify 无 sanitize 实现；静态渲染只需透传 HTML。
vi.mock('dompurify', () => ({ default: { sanitize: (s: string) => s } }))

import { DemoConsole } from '../DemoConsole'
import { DEMO_SESSIONS, isBootFailure } from './demo'

describe('isBootFailure', () => {
  it('网络不可达（TypeError）与 CDN HTML 回退（SyntaxError）判定为可降级演示', () => {
    expect(isBootFailure(new SyntaxError('Unexpected token < in JSON'))).toBe(true)
    expect(isBootFailure(new TypeError('Failed to fetch'))).toBe(true)
  })

  it('本地服务端业务错误保持显式报错，不降级', () => {
    expect(isBootFailure(new Error('GET /openarch/config → 500 boom'))).toBe(false)
    expect(isBootFailure(new Error('未找到 OpenArch agent'))).toBe(false)
    expect(isBootFailure('boom')).toBe(false)
  })
})

describe('DEMO_SESSIONS', () => {
  it('至少一个示例会话，消息与交付物结构完整', () => {
    expect(DEMO_SESSIONS.length).toBeGreaterThan(0)
    for (const s of DEMO_SESSIONS) {
      expect(s.id).toBeTruthy()
      expect(s.name).toBeTruthy()
      expect(s.messages.length).toBeGreaterThan(0)
      for (const m of s.messages) {
        expect(['user', 'assistant']).toContain(m.role)
        expect(m.text.trim().length).toBeGreaterThan(0)
      }
      for (const f of s.files) {
        expect(f.name).toBeTruthy()
        expect(f.path).toContain('/')
        expect(f.content.trim().length).toBeGreaterThan(0)
      }
    }
  })

  it('示例内容对齐产品叙事：架构设计工作单', () => {
    const allText = DEMO_SESSIONS.map((s) =>
      [s.name, ...s.messages.map((m) => m.text), ...s.files.map((f) => f.content)].join('\n'),
    ).join('\n')
    expect(allText).toContain('架构')
    expect(allText).toContain('WAF')
  })
})

describe('DemoConsole', () => {
  it('静态渲染含演示标注、三区结构与默认选中会话', () => {
    const html = renderToStaticMarkup(createElement(DemoConsole))
    expect(html).toContain('演示数据')
    expect(html).toContain('本地运行')
    expect(html).toContain('openarch web')
    expect(html).toContain('OpenArch')
    expect(html).toContain('交付物')
    expect(html).toContain('appbar')
    expect(html).toContain('sidebar')
    expect(html).toContain('chat')
    expect(html).toContain('files')
    expect(html).toContain(DEMO_SESSIONS[0]!.name)
  })
})
