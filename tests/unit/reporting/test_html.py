"""Tests for interactive HTML reporting."""

import networkx as nx
from pathlib import Path
from prism.models.finding import Finding
from prism.reporting.html import HtmlReporter

def test_generate_html_report(tmp_path: Path) -> None:
    """Test that the pyvis output handles the graph mapping properly."""
    reporter = HtmlReporter()
    
    graph = nx.DiGraph()
    graph.add_node("GET /users", method="GET", url="/users")
    graph.add_node("POST /users", method="POST", url="/users")
    graph.add_edge("POST /users", "GET /users", identifier="123")
    
    f1 = Finding(id="f1", title="Title", description="Desc", cwe_id="CWE", cvss_vector="CVSS")
    
    out_path = tmp_path / "report.html"
    reporter.generate((f1,), graph, str(out_path))
    
    assert out_path.exists()
    content = out_path.read_text()
    
    assert "<html" in content
    assert "vis-network" in content
    assert "POST /users" in content
