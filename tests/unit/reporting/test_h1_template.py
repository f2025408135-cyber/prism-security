"""Tests for HackerOne template."""

from pathlib import Path
from prism.models.finding import Finding
from prism.reporting.h1_template import H1TemplateGenerator

def test_generate_h1_template(tmp_path: Path) -> None:
    """Test generating a bug bounty format template."""
    f1 = Finding(id="f1", title="Title", description="This is bad.", cwe_id="CWE-1", cvss_vector="CVSS:3")
    
    reporter = H1TemplateGenerator()
    out_path = tmp_path / "h1.md"
    
    reporter.generate(f1, str(out_path))
    
    content = out_path.read_text()
    
    assert "## Summary" in content
    assert "This is bad." in content
    assert "## Steps To Reproduce" in content
    assert "N/A" in content  # No poc provided
    assert "CVSS:3" in content
