from openarch.tools.drawio import flowchart_to_drawio
from openarch.tools.mermaid import parse_flowchart

MERMAID = "flowchart TD\n  web[Web 前端] --> slb[SLB]\n  slb --> db[(数据库)]\n"

def test_xml_contains_vertices_and_edges():
    xml = flowchart_to_drawio(parse_flowchart(MERMAID), title="电商架构")
    assert "<mxGraphModel" in xml and "</mxGraphModel>" in xml
    assert xml.count('vertex="1"') == 3
    assert xml.count('edge="1"') == 2

def test_labels_and_title_escaped():
    xml = flowchart_to_drawio(
        parse_flowchart("flowchart TD\n  a[A&B] --> b"), title="T<1>"
    )
    assert "A&amp;B" in xml
    assert "T&lt;1&gt;" in xml

def test_edge_labels_present():
    xml = flowchart_to_drawio(
        parse_flowchart("flowchart TD\n  a -->|主库| b"), title="t"
    )
    assert "主库" in xml
