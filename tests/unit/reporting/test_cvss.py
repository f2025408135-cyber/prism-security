"""Tests for CVSS calculation."""

import pytest
from prism.reporting.cvss import CVSSCalculator

def test_calculate_cvss() -> None:
    """Test mapping impacts based on heuristic rules."""
    calc = CVSSCalculator()
    
    # BOLA GET (Confidentiality High, Integrity None, Availability None)
    v1 = calc.calculate_vector("BOLA_CANDIDATE", "GET")
    assert "C:H/I:N/A:N" in v1
    
    # BFLA POST (Confidentiality High, Integrity High, Availability None)
    v2 = calc.calculate_vector("BFLA_CANDIDATE", "POST")
    assert "C:H/I:H/A:N" in v2
    
    # RACE DELETE (Confidentiality None, Integrity High, Availability High)
    v3 = calc.calculate_vector("RACE_CONDITION", "DELETE")
    assert "C:N/I:H/A:H" in v3
