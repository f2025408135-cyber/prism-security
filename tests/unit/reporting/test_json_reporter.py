"""Tests for JSON reporting."""

import json
from pathlib import Path
from prism.models.finding import Finding
from prism.reporting.json_reporter import JsonReporter

def test_generate_json_report(tmp_path: Path) -> None:
    """Test writing findings to JSON format."""
    f1 = Finding(id="f1", title="Title", description="Desc", cwe_id="CWE-1", cvss_vector="CVSS:3")
    f2 = Finding(id="f2", title="Title2", description="Desc2", cwe_id="CWE-2", cvss_vector="CVSS:3")
    
    reporter = JsonReporter()
    out_path = tmp_path / "report.json"
    
    reporter.generate((f1, f2), str(out_path))
    
    assert out_path.exists()
    
    with out_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data["findings_count"] == 2
    assert data["version"] == "1.0"
    assert data["findings"][0]["id"] == "f1"
