# 阿里云选型决策树（精简）

## 计算

- 容器化且需要编排 → ACK；简单无状态长驻 → ECS 弹性伸缩组
- 事件驱动/短任务/流量波动大 → 函数计算 FC
- GPU 推理 → ACK GPU 节点池 或 PAI-EAS

## 数据库

- 关系型、事务 → RDS MySQL/PostgreSQL（默认主备高可用版）
- 海量并发读 + 弹性 → PolarDB
- 文档/宽表、超大规模 → MongoDB/Lindorm
- 缓存 → Redis（集群版按 QPS 选规格）

## 消息

- 顺序/事务/延迟消息 → RocketMQ
- 大数据流接入、日志 → Kafka / 日志服务 SLS
- 仅异步解耦、轻量 → MNS

## 网络

- 公网入口 → SLB/ALB（+ WAF + DDoS 防护）
- 多环境隔离 → VPC + 交换机划分；混合云 → 高速通道/VPN 网关
- 全球加速 → GA

原则：托管服务优先于自建；同一方案内避免引入能力重叠的组件。
