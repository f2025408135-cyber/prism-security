"""Tests for the database repository."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from prism.db.engine import DatabaseEngine
from prism.db.models import Base, PrincipalRecord
from prism.db.repository import PrincipalRepository
from prism.exceptions import StorageError

import pytest_asyncio

@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Provide an in-memory async database session."""
    engine = DatabaseEngine("sqlite+aiosqlite:///:memory:")
    
    # Create tables
    async with engine._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    session = engine.get_session()
    yield session
    
    await session.close()
    await engine.close()

@pytest.mark.asyncio
async def test_principal_repository_save_and_get(db_session: AsyncSession) -> None:
    """Test saving and retrieving a principal record."""
    repo = PrincipalRepository(db_session)
    record = PrincipalRecord(id="p1", name="alice", roles=["admin"])
    
    await repo.save(record)
    retrieved = await repo.get_by_id("p1")
    
    assert retrieved is not None
    assert retrieved.id == "p1"
    assert retrieved.name == "alice"
    assert retrieved.roles == ["admin"]

@pytest.mark.asyncio
async def test_principal_repository_get_not_found(db_session: AsyncSession) -> None:
    """Test retrieving a non-existent principal."""
    repo = PrincipalRepository(db_session)
    retrieved = await repo.get_by_id("missing")
    assert retrieved is None
