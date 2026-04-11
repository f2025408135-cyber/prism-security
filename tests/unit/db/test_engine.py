"""Tests for the database engine."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from prism.db.engine import DatabaseEngine
from prism.exceptions import StorageError

@pytest.mark.asyncio
async def test_database_engine_lifecycle() -> None:
    """Test engine initialization and session creation."""
    engine = DatabaseEngine("sqlite+aiosqlite:///:memory:")
    session = engine.get_session()
    
    assert isinstance(session, AsyncSession)
    await session.close()
    await engine.close()

def test_database_engine_invalid_url() -> None:
    """Test engine initialization with an invalid URL."""
    with pytest.raises(StorageError):
        # Missing dialect
        DatabaseEngine("invalid_url")
