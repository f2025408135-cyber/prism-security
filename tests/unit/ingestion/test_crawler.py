"""Tests for the Katana crawler wrapper."""

import json
import pytest
import asyncio
from unittest.mock import patch, MagicMock

from prism.ingestion.crawler import run_katana_crawler
from prism.exceptions import IngestionError

# Sample JSONL output from Katana
MOCK_KATANA_STDOUT = b"""
{"request": {"method": "GET", "endpoint": "https://api.example.com/admin?debug=true"}}
{"request": {"method": "GET", "endpoint": "https://api.example.com/admin?debug=false"}}
{"request": {"method": "POST", "endpoint": "https://api.example.com/login"}}
"""

@pytest.mark.asyncio
async def test_run_katana_crawler_success() -> None:
    """Test successful execution and parsing of Katana output."""
    
    # Create a mock process
    from unittest.mock import AsyncMock
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (MOCK_KATANA_STDOUT, b"")
    mock_process.returncode = 0

    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        endpoints = await run_katana_crawler("https://api.example.com")
        
    # Deduplication means we only get 1 GET to /admin and 1 POST to /login
    assert len(endpoints) == 2
    
    get_admin = next(e for e in endpoints if e.method == "GET")
    assert get_admin.url == "https://api.example.com/admin?debug=true"
    assert len(get_admin.parameters) == 1
    assert get_admin.parameters[0].name == "debug"
    assert get_admin.parameters[0].value == "true"

@pytest.mark.asyncio
async def test_run_katana_crawler_not_installed() -> None:
    """Test behavior when Katana is not installed (raises FileNotFoundError)."""
    with patch('asyncio.create_subprocess_exec', side_effect=FileNotFoundError("No such file")):
        with pytest.raises(IngestionError, match="Katana is not installed"):
            await run_katana_crawler("https://api.example.com")
