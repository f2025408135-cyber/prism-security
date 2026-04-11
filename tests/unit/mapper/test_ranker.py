"""Tests for the ranker."""

import pytest
from prism.mapper.inconsistency import AuthzInconsistency
from prism.mapper.classifier import ClassifiedInconsistency
from prism.mapper.ranker import InconsistencyRanker

def test_rank_inconsistencies() -> None:
    """Test sorting of inconsistencies by impact and confidence."""
    ranker = InconsistencyRanker()
    
    inc1 = AuthzInconsistency(
        principal_id="u1", identifier="1", accessible_endpoint="GET /users/1", denied_endpoint="GET /users", reason="A"
    )
    c1 = ClassifiedInconsistency(inconsistency=inc1, vuln_class="BOLA_CANDIDATE", confidence=0.8)
    
    inc2 = AuthzInconsistency(
        principal_id="u2", identifier="2", accessible_endpoint="DELETE /users/2", denied_endpoint="GET /users", reason="B"
    )
    c2 = ClassifiedInconsistency(inconsistency=inc2, vuln_class="BOLA_CANDIDATE", confidence=0.95)
    
    inc3 = AuthzInconsistency(
        principal_id="u3", identifier="3", accessible_endpoint="GET /users", denied_endpoint="GET /users/3", reason="C"
    )
    c3 = ClassifiedInconsistency(inconsistency=inc3, vuln_class="SCOPE_GAP_CANDIDATE", confidence=0.7)
    
    ranked = ranker.rank((c1, c2, c3))
    
    assert len(ranked) == 3
    # c2 is a DELETE BOLA, highest priority (10.0 class * 10.0 method * 0.95 conf = 95.0)
    assert ranked[0].inconsistency.principal_id == "u2"
    # c1 is a GET BOLA, second priority (10.0 class * 4.0 method * 0.8 conf = 32.0)
    assert ranked[1].inconsistency.principal_id == "u1"
    # c3 is a SCOPE GAP GET, lowest priority (6.0 class * 4.0 method * 0.7 conf = 16.8)
    assert ranked[2].inconsistency.principal_id == "u3"
