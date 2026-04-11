"""Tests for finding data models."""

import pytest
from prism.models.finding import Evidence, PoC, Finding

def test_evidence_creation() -> None:
    """Test creation of an Evidence model."""
    ev = Evidence(
        id="ev_1",
        description="Unathorized access attempt",
        request_excerpt="GET /admin",
        response_excerpt="200 OK"
    )
    
    assert ev.id == "ev_1"
    assert ev.request_excerpt == "GET /admin"

def test_poc_creation() -> None:
    """Test creation of a PoC model."""
    poc = PoC(steps=("curl -X GET /admin", "verify 200"))
    
    assert len(poc.steps) == 2

def test_finding_creation() -> None:
    """Test creation of a Finding model."""
    ev = Evidence(id="e1", description="d", request_excerpt="req", response_excerpt="res")
    poc = PoC(steps=("step1",))
    
    finding = Finding(
        id="f1",
        title="BOLA in Admin Panel",
        description="Direct object reference bypassed authz.",
        cwe_id="CWE-284",
        cvss_vector="CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N",
        evidence=(ev,),
        poc=poc
    )
    
    assert finding.id == "f1"
    assert finding.cwe_id == "CWE-284"
    assert len(finding.evidence) == 1
    assert finding.poc is not None
    assert finding.poc.steps[0] == "step1"

def test_finding_is_frozen() -> None:
    """Test that the Finding model is immutable."""
    finding = Finding(
        id="f", title="t", description="d",
        cwe_id="cwe", cvss_vector="cvss"
    )
    with pytest.raises(Exception):
        finding.title = "new title"  # type: ignore
