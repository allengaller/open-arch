from openarch.tools.mermaid import validate_mermaid

VALID = """flowchart TD
  web[Web 前端] --> slb[SLB]
  slb --> api{判断}
  api -->|是| db[(数据库)]
  api --> cache(缓存)
"""

def test_valid_diagram_passes():
    r = validate_mermaid(VALID)
    assert r.ok, r.errors

def test_missing_flowchart_header():
    r = validate_mermaid("  web[前端] --> slb[SLB]")
    assert not r.ok
    assert any("flowchart" in e for e in r.errors)

def test_invalid_direction():
    r = validate_mermaid("flowchart XX\n  a --> b")
    assert not r.ok
    assert any("方向" in e for e in r.errors)

def test_node_label_with_bracket_char_is_error():
    r = validate_mermaid("flowchart TD\n  a[x]y] --> b")
    assert not r.ok

def test_empty_diagram_is_error():
    r = validate_mermaid("flowchart TD")
    assert not r.ok
    assert any("节点" in e for e in r.errors)

def test_edge_creates_implicit_node():
    from openarch.tools.mermaid import parse_flowchart
    fc = parse_flowchart("flowchart LR\n  a --> b")
    assert fc.nodes["b"].text == ""
    assert fc.edges[0].src == "a" and fc.edges[0].dst == "b"
