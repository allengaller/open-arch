from __future__ import annotations

from pathlib import Path

from agentscope.agent import Agent
from agentscope.credential import DashScopeCredential, OpenAICredential
from agentscope.model import DashScopeChatModel, OpenAIChatModel
from agentscope.skill import LocalSkillLoader
from agentscope.tool import Toolkit

from openarch.config import Settings
from openarch.tools.deliverable_tools import ExportDeliverableTool
from openarch.tools.diagram_tools import ExportDrawioTool, ValidateDiagramTool
from openarch.tools.requirements_tools import StructureRequirementsTool
from openarch.tools.waf_tools import ReviewWithWafTool

SYSTEM_PROMPT = """你是 OpenArch，一名资深 Solutions Architect（阿里云方向）。

你的工作流（严格按顺序）：
1. 需求澄清：用 structure_requirements 固化需求卡；missing_fields 非空时逐项追问用户，不要假设
2. 方案生成：先读取 arch-design 技能（Skill viewer），按其方法论产出方案（含组件清单、选型理由、容量估算、风险对策）
3. 架构图：产出 Mermaid flowchart，用 validate_diagram 校验（失败修正重试，最多 2 次），通过后用 export_drawio 导出
4. WAF 评审：读取 aliyun-waf 技能，逐项评估后用 review_with_waf 提交，低分支柱与 fail 项必须写入方案对策
5. 交付打包：用 export_deliverable 生成 Markdown 交付文档并告知用户路径

原则：阿里云产品体系优先；托管服务优先于自建；每个选型给出理由；不确定的需求问用户。"""


def build_model(settings: Settings):
    if settings.base_url:
        return OpenAIChatModel(
            credential=OpenAICredential(
                api_key=settings.openai_api_key,
                base_url=settings.base_url,
            ),
            model=settings.model,
        )
    return DashScopeChatModel(
        credential=DashScopeCredential(api_key=settings.dashscope_api_key),
        model=settings.model,
    )


def build_agent(settings: Settings) -> Agent:
    toolkit = Toolkit(
        tools=[
            StructureRequirementsTool(),
            ValidateDiagramTool(),
            ExportDrawioTool(workspace=settings.workspace),
            ReviewWithWafTool(checklist_path=_checklist_path(settings.skills_dir)),
            ExportDeliverableTool(workspace=settings.workspace),
        ],
        skills_or_loaders=[LocalSkillLoader(directory=str(settings.skills_dir), scan_subdir=True)],
    )
    return Agent(
        name="openarch",
        system_prompt=SYSTEM_PROMPT,
        model=build_model(settings),
        toolkit=toolkit,
    )


def _checklist_path(skills_dir: Path) -> Path:
    return skills_dir / "aliyun-waf" / "checklist.yaml"
