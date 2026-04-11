"""Tests for the inconsistency classifier."""

import pytest
from prism.mapper.inconsistency import AuthzInconsistency
from prism.mapper.classifier import InconsistencyClassifier, ClassifiedInconsistency

def test_classify_bola() -> None:
    """Test classifying a BOLA candidate."""
    classifier = InconsistencyClassifier()
    
    inc = AuthzInconsistency(
        principal_id="u1",
        identifier="123",
        accessible_endpoint="GET /users/123",
        denied_endpoint="GET /users",
        reason="Forbidden at source but authorized at destination (BOLA candidate)."
    )
    
    classified = classifier.classify((inc,))
    
    assert len(classified) == 1
    assert classified[0].vuln_class == "BOLA_CANDIDATE"
    assert classified[0].confidence == 0.8

def test_classify_destructive_bola() -> None:
    """Test classifying a destructive BOLA candidate."""
    classifier = InconsistencyClassifier()
    
    inc = AuthzInconsistency(
        principal_id="u1",
        identifier="123",
        accessible_endpoint="DELETE /users/123",
        denied_endpoint="GET /users",
        reason="Forbidden at source but authorized at destination (BOLA candidate)."
    )
    
    classified = classifier.classify((inc,))
    
    assert len(classified) == 1
    assert classified[0].vuln_class == "BOLA_CANDIDATE"
    assert classified[0].confidence == 0.95

def test_classify_bfla() -> None:
    """Test classifying a BFLA candidate."""
    classifier = InconsistencyClassifier()
    
    inc = AuthzInconsistency(
        principal_id="u1",
        identifier="123",
        accessible_endpoint="POST /users",
        denied_endpoint="GET /users",
        reason="Random reason"
    )
    
    classified = classifier.classify((inc,))
    
    assert len(classified) == 1
    assert classified[0].vuln_class == "BFLA_CANDIDATE"
    assert classified[0].confidence == 0.85
