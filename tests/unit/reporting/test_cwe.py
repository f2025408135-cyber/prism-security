"""Tests for CWE mapping."""

import pytest
from prism.reporting.cwe import CWEMapper

def test_map_cwe() -> None:
    """Test correct CWE IDs are returned."""
    mapper = CWEMapper()
    
    assert mapper.map_cwe("BOLA_CANDIDATE") == "CWE-639"
    assert mapper.map_cwe("BFLA_CANDIDATE") == "CWE-285"
    assert mapper.map_cwe("RACE_CONDITION") == "CWE-362"
    assert mapper.map_cwe("SCOPE_GAP_CANDIDATE") == "CWE-200"
    assert mapper.map_cwe("UNKNOWN_VULN") == "CWE-284"
