import json

from openarch.tools.requirements_tools import StructureRequirementsTool

OPTIONAL = ["scale", "availability_target", "budget_range", "compliance", "existing_systems"]


async def test_full_card_has_no_missing():
    tool = StructureRequirementsTool()
    out = json.loads(
        (
            await tool(
                business_scenario="电商网站",
                scale="日均 10 万订单",
                availability_target="99.95%",
                budget_range="月 2 万元以内",
                compliance="需支持等保三级",
                existing_systems="单体 PHP 应用",
            )
        ).content[0].text
    )
    assert out["card"]["business_scenario"] == "电商网站"
    assert out["missing_fields"] == []


async def test_partial_card_lists_missing():
    tool = StructureRequirementsTool()
    out = json.loads((await tool(business_scenario="数据平台")).content[0].text)
    assert out["missing_fields"] == OPTIONAL


async def test_registers_into_real_toolkit():
    from agentscope.tool import Toolkit

    toolkit = Toolkit(tools=[StructureRequirementsTool()])
    schemas = await toolkit.get_tool_schemas()
    fn = {s["function"]["name"]: s["function"] for s in schemas}["structure_requirements"]
    assert fn["parameters"]["properties"]["scale"]["description"] == "规模/并发/数据量"
