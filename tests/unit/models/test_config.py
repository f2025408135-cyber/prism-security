"""Tests for configuration data models."""

import pytest
from pydantic import ValidationError
from prism.models.config import Config, ScanConfig

def test_scan_config_creation() -> None:
    """Test creation of a ScanConfig model."""
    config = ScanConfig(
        target_url="https://api.example.com",
        in_scope_patterns=("https://api.example.com/*",)
    )
    
    assert config.target_url == "https://api.example.com"
    assert config.concurrency == 10  # default value
    assert len(config.in_scope_patterns) == 1

def test_config_creation() -> None:
    """Test creation of a Config model."""
    scan = ScanConfig(target_url="https://test.com")
    config = Config(workspace_dir="/tmp/prism", scan_config=scan)
    
    assert config.workspace_dir == "/tmp/prism"
    assert config.scan_config.target_url == "https://test.com"

def test_config_is_frozen() -> None:
    """Test that the Config model is immutable."""
    config = Config()
    with pytest.raises(ValidationError):
        config.workspace_dir = "/new"  # type: ignore
