"""Tests for race condition probability scorer."""

import pytest
from prism.race.scorer import RaceProbabilityScorer

def test_score_endpoint() -> None:
    """Test heuristic scoring of endpoints."""
    scorer = RaceProbabilityScorer()
    
    # Financial endpoints should score highest
    assert scorer.score_endpoint("POST", "https://api.com/checkout", False) > 0.6
    
    # State transitions should score high
    assert scorer.score_endpoint("PUT", "https://api.com/activate/123", False) > 0.4
    
    # Single-use operations get a bump
    assert scorer.score_endpoint("DELETE", "https://api.com/item/1", True) > 0.5
    
    # Read-only operations are zero risk
    assert scorer.score_endpoint("GET", "https://api.com/users", True) == 0.0
