"""Tests for Evidence Chain formatting."""

import pytest
from prism.models.finding import Evidence
from prism.reporting.evidence import EvidenceBuilder

def test_format_evidence_chain() -> None:
    """Test markdown formatting of evidence."""
    builder = EvidenceBuilder()
    
    ev = Evidence(id="1", description="Test evidence", request_excerpt="GET /api", response_excerpt="404 Not Found")
    output = builder.format_evidence_chain((ev,))
    
    assert "### Evidence Chain" in output
    assert "#### [1] Test evidence" in output
    assert "**Request:**" in output
    assert "GET /api" in output
    assert "**Response Excerpt:**" in output
    assert "404 Not Found" in output

def test_format_evidence_chain_empty() -> None:
    """Test handling empty evidence."""
    builder = EvidenceBuilder()
    output = builder.format_evidence_chain(())
    
    assert "No concrete HTTP evidence provided." in output
