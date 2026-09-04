// 演示模式：Meoo CDN 等纯静态托管下无后端，启动失败时以内置示例数据渲染三区界面。
export function isBootFailure(e: unknown): boolean {
  // TypeError：fetch 网络不可达；SyntaxError：CDN 把未知路径回退成 index.html，res.json() 解析失败。
  return e instanceof SyntaxError || e instanceof TypeError
}

export interface DemoMessage {
  role: 'user' | 'assistant'
  text: string
}

export interface DemoFile {
  name: string
  path: string
  content: string
}

export interface DemoSession {
  id: string
  name: string
  messages: DemoMessage[]
  files: DemoFile[]
}

const ECOMMERCE_MERMAID = `flowchart LR
  U[用户] --> CDN[CDN]
  CDN --> WAF[WAF 防护]
  WAF --> SLB[SLB 负载均衡]
  SLB --> GW[API 网关]
  GW --> ORD[订单服务]
  GW --> STK[库存服务]
  GW --> PAY[支付服务]
  ORD --> DB[(MySQL 主从)]
  STK --> REDIS[(Redis)]
  ORD --> MQ[消息队列]
  MQ --> NTF[通知/积分服务]`

const ECOMMERCE_SCENARIO: DemoSession = {
  id: 'demo-ecommerce',
  name: '电商高可用架构设计',
  messages: [
    {
      role: 'user',
      text: '为一个日均 10 万单的电商系统设计高可用架构。大促期间流量预计涨 5 倍，预算有限，团队 6 人。',
    },
    {
      role: 'assistant',
      text: `已完成需求澄清与方案生成，要点如下：

**需求澄清（已确认）**
- 目标可用性：核心下单链路 ≥ 99.95%
- 大促容量：峰值流量按日常 5 倍估算，读多写少
- 约束：预算有限，优先托管服务，团队偏好低运维复杂度

**总体方案**
1. 接入层：CDN + WAF + SLB，多可用区容灾
2. 服务层：订单 / 库存 / 支付拆分为独立服务，API 网关统一鉴权与限流
3. 数据层：MySQL 主从读写分离，Redis 缓存热点商品，库存走 Redis 预扣
4. 异步化：积分、通知等非核心链路走消息队列削峰

\`\`\`mermaid
${ECOMMERCE_MERMAID}
\`\`\`

**WAF 评审要点**
- 可靠性：网关配置限流与熔断，主从切换演练纳入上线前检查
- 安全：全链路 HTTPS，数据库不暴露公网，网关统一鉴权
- 成本：大促按量扩容、日常缩容，避免长期为峰值付费

下一步：输入「生成评审报告」可产出完整 WAF 评审文档，或继续调整方案。`,
    },
  ],
  files: [
    {
      name: '电商高可用架构方案.md',
      path: '交付物/电商高可用架构方案.md',
      content: `# 电商高可用架构方案

## 背景与目标
日均 10 万单，大促峰值按 5 倍估算；核心下单链路可用性目标 ≥ 99.95%。

## 关键决策
| 层 | 决策 | 理由 |
| --- | --- | --- |
| 接入 | CDN + WAF + SLB 多可用区 | 抗流量放大与攻击，托管低运维 |
| 服务 | 订单 / 库存 / 支付独立部署 | 故障隔离，独立扩容 |
| 数据 | MySQL 主从 + Redis 预扣库存 | 读扩展 + 削减热点行竞争 |
| 异步 | 消息队列承接非核心链路 | 大促削峰，保护下单主链路 |

## 演进路径
先按上述最小可用架构上线，大促前压测并扩容；后续按量引入读写分离中间件与多活。
`,
    },
    {
      name: '系统架构图.mermaid',
      path: '交付物/系统架构图.mermaid',
      content: `\`\`\`mermaid
${ECOMMERCE_MERMAID}
\`\`\``,
    },
    {
      name: 'WAF评审报告.md',
      path: '交付物/WAF评审报告.md',
      content: `# WAF 架构评审报告（示例）

**评审对象**：电商高可用架构方案 · **结论**：有条件通过

| 维度 | 评估 | 关键建议 |
| --- | --- | --- |
| 可靠性 | 通过 | 网关限流 + 熔断；主从切换演练 |
| 安全 | 通过 | 全链路 HTTPS；数据库不暴露公网 |
| 成本 | 关注 | 大促临时扩容，日常缩容 |
| 可演进 | 通过 | 服务边界清晰，可平滑拆分读服务 |
`,
    },
  ],
}

const MULTITENANT: DemoSession = {
  id: 'demo-multitenant',
  name: 'SaaS 多租户隔离方案',
  messages: [
    {
      role: 'user',
      text: '我们的 B 端 SaaS 要支持 200 家企业客户，数据隔离怎么做比较合适？',
    },
    {
      role: 'assistant',
      text: `三种主流隔离方案对比：

| 方案 | 隔离强度 | 成本 | 运维复杂度 | 适用 |
| --- | --- | --- | --- | --- |
| 独立数据库 | 强 | 高 | 高 | 强合规大客户 |
| 共享库独立 Schema | 中 | 中 | 中 | 中等规模 |
| 共享表 + tenant_id | 弱 | 低 | 低 | 起步阶段 |

**推荐**：200 家客户规模下，从「共享表 + tenant_id」起步，全链路强制租户过滤（ORM 中间件 + 行级校验），并为大客户预留迁移到独立库的路径。

**关键动作**
1. 所有表带 tenant_id 并建复合索引
2. 数据访问层统一注入租户上下文，禁止手写裸查询
3. 定期审计越权访问，准备租户级导出/迁移工具`,
    },
  ],
  files: [
    {
      name: '多租户隔离方案.md',
      path: '交付物/多租户隔离方案.md',
      content: `# SaaS 多租户数据隔离方案（示例）

## 结论
共享表 + tenant_id 起步，预留独立库演进路径。

## 实施要点
- 全表 tenant_id + 复合索引
- ORM 中间件统一注入租户上下文
- 行级校验 + 越权访问审计
- 租户级导出 / 迁移工具预案
`,
    },
  ],
}

export const DEMO_SESSIONS: DemoSession[] = [ECOMMERCE_SCENARIO, MULTITENANT]
