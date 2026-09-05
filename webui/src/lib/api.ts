const USER_ID = 'local'
const JSON_HEADERS: Record<string, string> = {
  'Content-Type': 'application/json',
  'X-User-ID': USER_ID,
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(path, {
    ...init,
    headers: { ...JSON_HEADERS, ...((init?.headers as Record<string, string>) ?? {}) },
  })
  if (!resp.ok) {
    const detail = await resp.text().catch(() => '')
    throw new Error(`${init?.method ?? 'GET'} ${path} → ${resp.status} ${detail.slice(0, 200)}`)
  }
  return (await resp.json()) as T
}

export interface OpenArchConfig {
  model: string
}

export interface SessionSummary {
  id: string
  name: string
  status: string
}

export interface DirectoryEntryRaw {
  name: string
  is_dir: boolean
  size_bytes: number | null
  updated_at: string | null
}

export interface SkillPack {
  name: string
  description: string
  files: string[]
}

export const api = {
  config: () => req<OpenArchConfig>('/openarch/config'),

  listSkills: () => req<{ skills: SkillPack[] }>('/openarch/skills'),

  skillText: async (pack: string, path: string): Promise<string> => {
    const encoded = path.split('/').map(encodeURIComponent).join('/')
    const resp = await fetch(
      `/openarch/skills/${encodeURIComponent(pack)}/${encoded}`,
      { headers: { 'X-User-ID': USER_ID } },
    )
    if (!resp.ok) throw new Error(`读取知识文件失败：HTTP ${resp.status}`)
    return resp.text()
  },

  agentId: async (): Promise<string> => {
    const data = await req<{ agents: { id: string; data: { name: string } }[] }>('/agent/')
    const agent = data.agents.find((a) => a.data.name === 'OpenArch')
    if (!agent) throw new Error('未找到 OpenArch agent——请确认服务端种子已执行（openarch web 启动时会自动执行）')
    return agent.id
  },

  credentialId: async (): Promise<string> => {
    const data = await req<{ credentials: { id: string; data: { type: string } }[] }>('/credential/')
    const cred = data.credentials.find(
      (c) => c.data.type === 'dashscope_credential' || c.data.type === 'openai_credential',
    )
    if (!cred) throw new Error('未找到已种子凭证——请重新执行 openarch web')
    return cred.id
  },

  listSessions: (agentId: string) =>
    req<{ sessions: { session: { id: string; config: { name: string } }; status: string }[] }>(
      `/sessions/?agent_id=${encodeURIComponent(agentId)}`,
    ),

  createSession: (agentId: string, credentialId: string, model: string) =>
    req<{ session_id: string }>('/sessions/', {
      method: 'POST',
      body: JSON.stringify({
        agent_id: agentId,
        chat_model_config: { type: 'chat', credential_id: credentialId, model, parameters: {} },
      }),
    }),

  listMessages: (agentId: string, sessionId: string) =>
    req<{ messages: unknown[]; is_running: boolean; has_more: boolean }>(
      `/sessions/${encodeURIComponent(sessionId)}/messages?agent_id=${encodeURIComponent(agentId)}`,
    ),

  chat: (agentId: string, sessionId: string, text: string) =>
    req<unknown>('/chat/', {
      method: 'POST',
      body: JSON.stringify({
        agent_id: agentId,
        session_id: sessionId,
        input: { role: 'user', name: 'user', content: [{ type: 'text', text }] },
      }),
    }),

  interrupt: (agentId: string, sessionId: string) =>
    req<unknown>(
      `/sessions/${encodeURIComponent(sessionId)}/interrupt?agent_id=${encodeURIComponent(agentId)}`,
      { method: 'POST' },
    ),

  listDirectory: (agentId: string, sessionId: string, path: string) =>
    req<{ path: string; entries: DirectoryEntryRaw[] }>(
      `/workspace/directories?agent_id=${encodeURIComponent(agentId)}&session_id=${encodeURIComponent(sessionId)}&path=${encodeURIComponent(path)}`,
    ),

  fileText: async (agentId: string, sessionId: string, path: string): Promise<string> => {
    const resp = await fetch(
      `/workspace/files?agent_id=${encodeURIComponent(agentId)}&session_id=${encodeURIComponent(sessionId)}&path=${encodeURIComponent(path)}`,
      { headers: { 'X-User-ID': USER_ID } },
    )
    if (!resp.ok) throw new Error(`读取文件失败：HTTP ${resp.status}`)
    return resp.text()
  },

  downloadUrl: (agentId: string, sessionId: string, path: string) =>
    `/workspace/files?agent_id=${encodeURIComponent(agentId)}&session_id=${encodeURIComponent(sessionId)}&path=${encodeURIComponent(path)}&download=true`,
}
