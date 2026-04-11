"""Tests for PoC generation."""

import pytest
from prism.models.finding import Evidence
from prism.reporting.poc import PoCGenerator

def test_generate_poc_bola() -> None:
    """Test generating a BOLA PoC."""
    ev = Evidence(id="1", description="desc", request_excerpt="GET /api/users/2", response_excerpt="200 OK Bob")
    generator = PoCGenerator()
    
    poc = generator.generate_poc("BOLA_CANDIDATE", (ev,))
    
    assert poc is not None
    assert len(poc.steps) == 2
    assert "Step A (Attack)" in poc.steps[0]
    assert "curl -X GET '/api/users/2'" in poc.steps[0]
    assert "Step B (Verify)" in poc.steps[1]

def test_generate_poc_race() -> None:
    """Test generating a Race Condition PoC."""
    ev1 = Evidence(id="1", description="d", request_excerpt="POST /pay", response_excerpt="200 OK")
    ev2 = Evidence(id="2", description="d", request_excerpt="POST /pay", response_excerpt="200 OK")
    
    generator = PoCGenerator()
    poc = generator.generate_poc("RACE_CONDITION", (ev1, ev2))
    
    assert poc is not None
    assert len(poc.steps) == 3
    assert "Step A (Setup): Prepare 2 concurrent" in poc.steps[0]
    assert "curl -X POST '/pay'" in poc.steps[1]

def test_generate_poc_empty() -> None:
    """Test handling empty evidence."""
    generator = PoCGenerator()
    poc = generator.generate_poc("UNKNOWN", ())
    
    assert poc is None
