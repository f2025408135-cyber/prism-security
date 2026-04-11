"""Tests for object identifier extraction."""

import json
from prism.mapper.identifier import IdentifierExtractor
from prism.models.authz import AuthzDecision

def test_extract_uuid() -> None:
    """Test extracting standard UUIDv4 strings."""
    extractor = IdentifierExtractor()
    decision = AuthzDecision(
        endpoint_url="/test", endpoint_method="GET", principal_id="u1",
        http_status=200, is_authorized=True, timing_ms=10.0
    )
    
    body = '{"data": "user created", "id": "123e4567-e89b-12d3-a456-426614174000"}'
    ids = extractor.extract(decision, body)
    
    assert "123e4567-e89b-12d3-a456-426614174000" in ids

def test_extract_json_key() -> None:
    """Test extracting integer IDs from known JSON keys."""
    extractor = IdentifierExtractor()
    decision = AuthzDecision(
        endpoint_url="/test", endpoint_method="GET", principal_id="u1",
        http_status=200, is_authorized=True, timing_ms=10.0
    )
    
    body = '{"user": {"id": 105, "name": "alice"}, "slug": "alice-test-slug"}'
    ids = extractor.extract(decision, body)
    
    assert "105" in ids
    assert "alice-test-slug" in ids

def test_extract_unauthorized_returns_empty() -> None:
    """Test that unauthorized decisions don't yield identifiers."""
    extractor = IdentifierExtractor()
    decision = AuthzDecision(
        endpoint_url="/test", endpoint_method="GET", principal_id="u1",
        http_status=403, is_authorized=False, timing_ms=10.0
    )
    
    body = '{"error": "Forbidden", "id": "123"}'
    ids = extractor.extract(decision, body)
    
    assert len(ids) == 0
