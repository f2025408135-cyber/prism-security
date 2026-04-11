"""Tests for timing window analysis."""

import pytest

from prism.models.authz import AuthzDecision
from prism.race.timer import TimingAnalyzer, TimingWindow

def test_measure_timing_window() -> None:
    """Test statistical aggregation of execution times."""
    analyzer = TimingAnalyzer()
    url = "https://api.com/heavy-calc"
    
    d1 = AuthzDecision(endpoint_url=url, endpoint_method="POST", principal_id="u1", http_status=200, is_authorized=True, timing_ms=10.0)
    d2 = AuthzDecision(endpoint_url=url, endpoint_method="POST", principal_id="u1", http_status=200, is_authorized=True, timing_ms=15.0)
    d3 = AuthzDecision(endpoint_url=url, endpoint_method="POST", principal_id="u1", http_status=200, is_authorized=True, timing_ms=5.0)
    
    window = analyzer.measure_window(url, [d1, d2, d3])
    
    assert window is not None
    assert window.min_ms == 5.0
    assert window.max_ms == 15.0
    assert window.median_ms == 10.0
    assert window.is_viable is True

def test_measure_timing_window_not_viable() -> None:
    """Test timing window that is too fast to exploit generically."""
    analyzer = TimingAnalyzer()
    url = "https://api.com/fast"
    
    d1 = AuthzDecision(endpoint_url=url, endpoint_method="GET", principal_id="u1", http_status=200, is_authorized=True, timing_ms=1.0)
    d2 = AuthzDecision(endpoint_url=url, endpoint_method="GET", principal_id="u1", http_status=200, is_authorized=True, timing_ms=2.0)
    
    window = analyzer.measure_window(url, [d1, d2])
    
    assert window is not None
    assert window.median_ms == 1.5
    assert window.is_viable is False
