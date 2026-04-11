"""Async database engine and session management."""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from prism.exceptions import StorageError

logger = structlog.get_logger(__name__)


class DatabaseEngine:
    """Manages the SQLAlchemy async engine and session factory.

    Attributes:
        db_url: The database URL (e.g., sqlite+aiosqlite:///workspace.db).
    """

    def __init__(self, db_url: str) -> None:
        """Initialize the database engine.

        Args:
            db_url: The connection string for the database.
        """
        self.db_url = db_url
        try:
            self._engine = create_async_engine(
                self.db_url,
                echo=False,
                connect_args={"check_same_thread": False} if "sqlite" in self.db_url else {}
            )
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        except Exception as e:
            logger.error("db_engine_init_failed", url=self.db_url, error=str(e))
            raise StorageError(f"Failed to initialize database engine: {e}") from e

    def get_session(self) -> AsyncSession:
        """Get a new database session.

        Returns:
            An AsyncSession instance.
            
        Raises:
            StorageError: If the session factory fails to create a session.
        """
        try:
            return self._session_factory()
        except Exception as e:
            logger.error("db_session_creation_failed", error=str(e))
            raise StorageError("Failed to create database session.") from e

    async def close(self) -> None:
        """Dispose of the database engine."""
        try:
            await self._engine.dispose()
        except Exception as e:
            logger.error("db_engine_close_failed", error=str(e))
            raise StorageError("Failed to close database engine.") from e
