# 常见场景参考模式（阿里云）

## Web 应用（交易/内容类）

SLB/ALB → 无状态应用（ECS 弹性伸缩组 / ACK）→ RDS PostgreSQL/MySQL（主备）
+ Redis 缓存 + OSS 静态资源 + CDN；异步任务走 RocketMQ；入口挂 WAF。
读多写少先加缓存与读写分离；峰值明显用 ESSD AutoPL 与弹性伸缩。

## 数据平台

DataWorks 同步 → OSS 数据湖（DLF 元数据）→ MaxCompute/EMR 加工 →
Hologres/StarRocks 服务化查询 → Quick BI。批流一体按时效要求选 Flink。

## AI 推理服务

PAI-EAS 或自建：GPU 节点池（ACK）+ 网关（自定义指标弹性伸缩）+ Cache 相同请求去重 +
模型工件 OSS + Prometheus/Grafana 观测。大流量场景评估 PD 分离与量化。

## 模式选择原则

先匹配最接近的参考模式做起点，再按需求卡逐项裁剪；每处偏离参考模式都要写明理由。
