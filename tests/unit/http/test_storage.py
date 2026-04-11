"""Tests for the raw traffic storage engine."""

import json
from pathlib import Path
from prism.http.storage import TrafficStorage

def test_traffic_storage_store_and_load(tmp_path: Path) -> None:
    """Test storing and loading traffic correctly masks tokens."""
    storage = TrafficStorage(str(tmp_path))
    
    kwargs = {
        "method": "POST",
        "url": "https://api.example.com/v1/auth",
        "headers": {"Authorization": "Bearer super_secret_token_12345"},
        "json": {"username": "admin"}
    }
    
    exchange_id = storage.store(
        principal_id="user_1",
        request_kwargs=kwargs,
        status_code=200,
        response_headers=(("Content-Type", "application/json"),),
        response_body='{"status": "ok"}',
        timing_ms=15.5
    )
    
    assert exchange_id is not None
    
    # Load back and verify masking
    records = storage.load_all()
    assert len(records) == 1
    record = records[0]
    
    assert record["id"] == exchange_id
    assert record["principal_id"] == "user_1"
    assert record["response"]["status_code"] == 200
    assert record["response"]["timing_ms"] == 15.5
    
    headers = record["request"]["headers"]
    assert "super_secret" not in headers["Authorization"]
    assert "..." in headers["Authorization"]
