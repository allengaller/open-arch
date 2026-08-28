---
name: aliyun-waf
description: 阿里云 Well-Architected Framework 五支柱检查清单：架构方案评审时逐项评估并生成评分与风险清单
---

# 阿里云 Well-Architected 评审

对已完成初稿的架构方案执行评审：

1. 用 `review_with_waf` 工具的清单（`skills/aliyun-waf/checklist.yaml`）逐项对照方案：
   - **pass**：方案已明确覆盖，写明 evidence（方案中的对应设计）
   - **risk**：部分覆盖或依赖假设，写 evidence + recommendation
   - **fail**：完全未覆盖，写 evidence（缺失说明）+ recommendation
2. 所有条目都必须给出结论（工具会拒绝缺失/未知/重复条目）
3. 评审结论中：score < 0.6 的支柱和全部 fail 项必须在方案"关键风险与对策"中给出改进措施

清单基于阿里云公开的 Well-Architected Framework 文档整理（MVP 精简版，每支柱 5 项）。
