"""Repository for standard async database operations."""

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from prism.db.models import PrincipalRecord
from prism.exceptions import StorageError

logger = structlog.get_logger(__name__)


class PrincipalRepository:
    """Handles persistence of Principal records."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.

        Args:
            session: The SQLAlchemy async session to use.
        """
        self._session = session

    async def save(self, record: PrincipalRecord) -> None:
        """Save a PrincipalRecord to the database.

        Args:
            record: The PrincipalRecord to save.

        Raises:
            StorageError: If the database operation fails.
        """
        try:
            self._session.add(record)
            await self._session.commit()
        except Exception as e:
            await self._session.rollback()
            logger.error("principal_save_failed", principal_id=record.id, error=str(e))
            raise StorageError(f"Failed to save principal {record.id}") from e

    async def get_by_id(self, principal_id: str) -> PrincipalRecord | None:
        """Retrieve a PrincipalRecord by its ID.

        Args:
            principal_id: The unique identifier.

        Returns:
            The PrincipalRecord if found, else None.

        Raises:
            StorageError: If the query fails.
        """
        try:
            stmt = select(PrincipalRecord).where(PrincipalRecord.id == principal_id)
            result = await self._session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            logger.error("principal_get_failed", principal_id=principal_id, error=str(e))
            raise StorageError(f"Failed to retrieve principal {principal_id}") from e
