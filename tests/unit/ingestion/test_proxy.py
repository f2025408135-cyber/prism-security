"""Tests for the live traffic proxy addon."""

import pytest
from unittest.mock import MagicMock

from prism.ingestion.proxy import PrismMitmAddon

def test_prism_mitm_addon_request() -> None:
    """Test that the mitmproxy addon extracts correct endpoint models."""
    addon = PrismMitmAddon("api.example.com")
    
    # Mock HTTPFlow
    flow_mock = MagicMock()
    flow_mock.request.host = "api.example.com"
    flow_mock.request.method = "POST"
    flow_mock.request.url = "https://api.example.com/v1/users?role=admin"
    flow_mock.request.query.items.return_value = [("role", "admin")]
    flow_mock.request.headers.items.return_value = [
        ("User-Agent", "Test"),  # Should be ignored
        ("X-API-Key", "secret")  # Should be captured
    ]
    
    addon.request(flow_mock)
    
    assert len(addon.endpoints) == 1
    endpoint = next(iter(addon.endpoints))
    
    assert endpoint.method == "POST"
    assert endpoint.url == "https://api.example.com/v1/users?role=admin"
    assert len(endpoint.parameters) == 2
    
    param_names = [p.name for p in endpoint.parameters]
    assert "role" in param_names
    assert "X-API-Key" in param_names
    assert "User-Agent" not in param_names

def test_prism_mitm_addon_skips_wrong_host() -> None:
    """Test that requests to other hosts are ignored."""
    addon = PrismMitmAddon("api.example.com")
    
    flow_mock = MagicMock()
    flow_mock.request.host = "evil.com"
    
    addon.request(flow_mock)
    assert len(addon.endpoints) == 0

def test_prism_mitm_addon_deduplication() -> None:
    """Test that identical signatures are deduplicated."""
    addon = PrismMitmAddon("api.example.com")
    
    flow_mock1 = MagicMock()
    flow_mock1.request.host = "api.example.com"
    flow_mock1.request.method = "GET"
    flow_mock1.request.url = "https://api.example.com/status?v=1"
    flow_mock1.request.query.items.return_value = [("v", "1")]
    flow_mock1.request.headers.items.return_value = []
    
    flow_mock2 = MagicMock()
    flow_mock2.request.host = "api.example.com"
    flow_mock2.request.method = "GET"
    flow_mock2.request.url = "https://api.example.com/status?v=2"
    flow_mock2.request.query.items.return_value = [("v", "2")]
    flow_mock2.request.headers.items.return_value = []
    
    addon.request(flow_mock1)
    addon.request(flow_mock2)
    
    assert len(addon.endpoints) == 1
