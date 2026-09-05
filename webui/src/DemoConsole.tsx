import { useState } from 'react'
import { DEMO_SESSIONS } from './lib/demo'
import { KnowledgePane } from './KnowledgePane'
import { MarkdownView } from './MarkdownView'

// 无后端时的演示控制台：布局类名与 App 三区一致（appbar / sidebar / chat / files）。
export function DemoConsole() {
  const [view, setView] = useState<'console' | 'knowledge'>('console')
  const [currentId, setCurrentId] = useState(DEMO_SESSIONS[0]!.id)
  const [preview, setPreview] = useState<{ name: string; text: string } | null>(null)
  const session = DEMO_SESSIONS.find((s) => s.id === currentId) ?? DEMO_SESSIONS[0]!

  return (
    <div className="app demo-app">
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
        <KnowledgePane notice="演示模式没有后端服务，知识库需本地运行 openarch web 后使用。" />
      ) : (
        <>
          <div className="demo-banner" title="本地运行 openarch web 获得完整功能">
            <span className="demo-banner-full">
              演示数据 · 本地运行 <code>openarch web</code> 获得完整功能
            </span>
            <span className="demo-banner-short">演示数据</span>
          </div>
          <aside className="sidebar">
            <div className="sidebar-head">
              <span className="brand">OpenArch</span>
              <button className="btn btn-primary" disabled title="演示模式下不可创建会话">
                + 新会话
              </button>
            </div>
            <ul className="session-list">
              {DEMO_SESSIONS.map((s) => (
                <li key={s.id}>
                  <button
                    className={s.id === currentId ? 'session-item active' : 'session-item'}
                    onClick={() => {
                      setCurrentId(s.id)
                      setPreview(null)
                    }}
                  >
                    <span className="session-name">{s.name}</span>
                  </button>
                </li>
              ))}
            </ul>
          </aside>
          <main className="chat">
            <div className="chat-scroll">
              {session.messages.map((m, i) => (
                <MarkdownView key={i} role={m.role} text={m.text} />
              ))}
            </div>
            <div className="chat-input">
              <textarea disabled placeholder="演示模式：本地运行 openarch web 即可真实对话" />
              <button className="btn btn-primary" disabled>
                发送
              </button>
            </div>
          </main>
          <aside className="files">
            <div className="files-head">
              <span>交付物</span>
              <span className="muted">示例</span>
            </div>
            <ul className="file-tree">
              <li>
                <details open>
                  <summary>交付物/</summary>
                  <ul className="file-tree nested">
                    {session.files.map((f) => (
                      <li key={f.path}>
                        <button className="file-link" onClick={() => setPreview({ name: f.name, text: f.content })}>
                          {f.name}
                        </button>
                      </li>
                    ))}
                  </ul>
                </details>
              </li>
            </ul>
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
        </>
      )}
    </div>
  )
}
