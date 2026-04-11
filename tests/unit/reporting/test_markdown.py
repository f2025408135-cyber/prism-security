"""Tests for Markdown reporting."""

from pathlib import Path
from prism.models.finding import Finding, PoC, Evidence
from prism.reporting.markdown import MarkdownReporter
from prism.reporting.evidence import EvidenceBuilder

def test_generate_markdown_report(tmp_path: Path) -> None:
    """Test generating markdown text."""
    ev = Evidence(id="e1", description="d", request_excerpt="r", response_excerpt="r2")
    poc = PoC(steps=("curl -X GET",))
    
    f1 = Finding(
        id="f1", title="Title", description="Desc", 
        cwe_id="CWE-1", cvss_vector="CVSS:3", poc=poc, evidence=(ev,)
    )
    
    builder = EvidenceBuilder()
    reporter = MarkdownReporter(builder)
    
    out_path = tmp_path / "report.md"
    reporter.generate((f1,), str(out_path))
    
    assert out_path.exists()
    content = out_path.read_text()
    
    assert "# PRISM Security Scan Report" in content
    assert "## Title" in content
    assert "curl -X GET" in content
    assert "### Evidence Chain" in content
