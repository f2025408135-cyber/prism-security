"""Tests for the normalizer."""

import pytest
from prism.ingestion.normalizer import normalize_and_deduplicate
from prism.models.endpoint import Endpoint, Parameter

def test_normalize_and_deduplicate() -> None:
    """Test URL normalization and deduplication."""
    e1 = Endpoint(method="GET", url="https://api.example.com//users/")
    e2 = Endpoint(method="GET", url="https://api.example.com/users")
    e3 = Endpoint(method="POST", url="https://api.example.com/users")
    e4 = Endpoint(method="GET", url="https://api.example.com/data?v=1")
    e5 = Endpoint(method="GET", url="https://api.example.com/data?v=1")
    
    endpoints = (e1, e2, e3, e4, e5)
    
    result = normalize_and_deduplicate(endpoints)
    
    assert len(result) == 3
    
    # GET /users
    assert any(e.url == "https://api.example.com/users" and e.method == "GET" for e in result)
    # POST /users
    assert any(e.url == "https://api.example.com/users" and e.method == "POST" for e in result)
    # GET /data?v=1
    assert any(e.url == "https://api.example.com/data?v=1" and e.method == "GET" for e in result)
