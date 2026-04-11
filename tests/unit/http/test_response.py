"""Tests for HTTP Response parser."""

import httpx
from unittest.mock import MagicMock
from prism.http.response import parse_response

def test_parse_response_json() -> None:
    """Test parsing a JSON response."""
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.headers = httpx.Headers({"Content-Type": "application/json"})
    mock_resp.text = '{"status": "ok"}'
    
    response = parse_response(mock_resp, 42.5)
    
    assert response.status_code == 200
    assert response.timing_ms == 42.5
    assert response.body_excerpt == '{"status": "ok"}'
    
    headers = dict(response.headers)
    assert headers["content-type"] == "application/json"

def test_parse_response_binary() -> None:
    """Test parsing a binary response gracefully."""
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.headers = httpx.Headers({"Content-Type": "image/png"})
    
    # Simulate a UnicodeDecodeError when accessing text
    type(mock_resp).text = property(lambda self: bytes([0x89, 0x50, 0x4e, 0x47]).decode('utf-8'))
    
    response = parse_response(mock_resp, 10.0)
    
    assert response.status_code == 200
    assert "[Binary data" in response.body_excerpt
    assert "image/png" in response.body_excerpt

def test_parse_response_truncation() -> None:
    """Test long body truncation."""
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.headers = httpx.Headers({"Content-Type": "text/plain"})
    
    long_string = "a" * 15000
    mock_resp.text = long_string
    
    response = parse_response(mock_resp, 5.0)
    
    assert len(response.body_excerpt) < 15000
    assert "...[truncated]..." in response.body_excerpt
