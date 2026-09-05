# 网络基础

## 私有网络

- **VPC（Virtual Private Cloud）**：账号内逻辑隔离的私网，一等公民是**网段规划**（CIDR）；VPC 间默认隔离
- **子网/交换机（Subnet/vSwitch）**：VPC 内的网段划分，通常按可用区 + 业务层（公网子网/应用子网/数据子网）切分
- **路由表（Route Table）**：决定流量走向；默认指向 VPC 内部，跨网段访问靠自定义路由（NAT 网关、对等连接、CEN/TGW 传播）
- **CIDR（Classless Inter-Domain Routing）**：如 `10.0.0.0/16`；前缀越长网段越小。**与 IDC 现网不重叠**是混合云的第一铁律
- **网关**：NAT 网关（内网主动访问公网）、Internet 网关/EIP（被动公网入口）、VPN 网关、专线网关

SA 场景提示：网段规划返工成本最高，方案里必须有 CIDR 规划表（模板见 cloud-frameworks/aliyun-landing-zone.md）。

## 负载均衡

| 维度 | 四层 LB | 七层 LB |
|---|---|---|
| 工作层级 | 传输层（IP+端口） | 应用层（HTTP/HTTPS） |
| 转发依据 | 连接目标地址端口 | URL/Header/Cookie |
| 典型能力 | 高性能 TCP/UDP 转发 | 卸载 TLS、WAF 联动、会话保持 |

- **健康检查（Health Check）**：探测后端可用性，摘除故障节点——高可用 checklist 的必查项（aliyun-waf REL-02）
- **会话保持（Sticky Session）**：同一客户端固定后端；有状态依赖的反面教材，优先改造成无状态 + 共享存储

## 接入与加速

- **DNS**：域名解析；智能解析按地域/运营商返回不同 IP，容灾切换靠低 TTL + 健康检查联动
- **CDN**：边缘缓存静态内容；关键词是**缓存命中率**（命中率高=回源少=源站压力小）与回源链路
- **专线（Physical Circuit）**：物理链路连 IDC 与 VPC，低时延稳定；**VPN**：公网加密隧道，快但质量波动。生产混合云标准做法：**专线为主、VPN 备份**
- **CEN/Transit Gateway**：云上骨干网，星型组网统一互通，替代 VPC 两两对等的网状拓扑

## 边界防护

- **安全组（Security Group）**：实例级有状态包过滤，**最小开放**是底线（aliyun-waf SEC-02）
- **网络 ACL**：子网级无状态过滤，粗粒度兜底
- **公网出入口收口**：入口统一 WAF/DDoS 防护层，出口统一 NAT + EIP 白名单——散落的公网 IP 是安全事故的温床
