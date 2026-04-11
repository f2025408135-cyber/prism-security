"""Tests for the HAR parser."""

import os
import pytest
from prism.ingestion.har import parse_har_file
from prism.exceptions import IngestionError

SPEC_PATH = os.path.join(os.path.dirname(__file__), "../../fixtures/specs/traffic.har")

def test_parse_har_valid_file() -> None:
    """Test parsing a valid HAR file and deduping."""
    endpoints = parse_har_file(SPEC_PATH)
    
    # There are 3 entries in HAR, but two are GET to /data, so deduplication
    # means we should only end up with 2 unique endpoints (GET /data and POST /submit)
    assert len(endpoints) == 2
    
    get_data = next(e for e in endpoints if e.method == "GET")
    assert get_data.url == "https://api.example.com/data?type=recent"
    assert len(get_data.parameters) == 2  # query 'type' + custom header
    
    param_names = [p.name for p in get_data.parameters]
    assert "type" in param_names
    assert "X-Custom-Header" in param_names
    assert "User-Agent" not in param_names  # standard header should be skipped
    
    post_submit = next(e for e in endpoints if e.method == "POST")
    assert post_submit.url == "https://api.example.com/submit"

def test_parse_har_invalid_file() -> None:
    """Test parsing an invalid or missing file raises IngestionError."""
    with pytest.raises(IngestionError):
        parse_har_file("nonexistent.har")
