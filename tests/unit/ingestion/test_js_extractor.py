"""Tests for the JS Extractor."""

import pytest
import respx
import httpx
from prism.ingestion.js_extractor import extract_endpoints_from_js
from prism.exceptions import IngestionError

MOCK_JS_BUNDLE = """
function init() {
    fetch("/api/v1/users");
    axios.post('/api/v1/auth/login', data);
    const oldUrl = "/rest/data/sync";
}
"""

@pytest.mark.asyncio
@respx.mock
async def test_extract_endpoints_from_js_success() -> None:
    """Test successful extraction of endpoints from a JS file."""
    js_url = "https://app.example.com/main.js"
    respx.get(js_url).mock(return_value=httpx.Response(200, text=MOCK_JS_BUNDLE))
    
    endpoints = await extract_endpoints_from_js(js_url, "https://api.example.com")
    
    assert len(endpoints) == 3
    urls = [e.url for e in endpoints]
    
    assert "https://api.example.com/api/v1/users" in urls
    assert "https://api.example.com/api/v1/auth/login" in urls
    assert "https://api.example.com/rest/data/sync" in urls
    
    for ep in endpoints:
        assert ep.method == "GET"  # default heuristic

@pytest.mark.asyncio
@respx.mock
async def test_extract_endpoints_from_js_http_error() -> None:
    """Test handling of HTTP errors when fetching JS."""
    js_url = "https://app.example.com/main.js"
    respx.get(js_url).mock(return_value=httpx.Response(404))
    
    with pytest.raises(IngestionError, match="Failed to fetch JS bundle"):
        await extract_endpoints_from_js(js_url, "https://api.example.com")
