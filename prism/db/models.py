"""SQLAlchemy ORM models for the PRISM framework."""

from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PrincipalRecord(Base):
    """ORM Model for storing Principal state.

    Attributes:
        id: The principal's unique identifier.
        name: The human-readable name.
        roles: JSON-encoded list of roles.
    """
    __tablename__ = "principals"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    roles = Column(JSON, nullable=False)


class AuthzDecisionRecord(Base):
    """ORM Model for storing AuthzDecision state.

    Attributes:
        id: Synthetic primary key.
        endpoint_url: The URL probed.
        endpoint_method: The HTTP method.
        principal_id: The ID of the principal making the request.
        http_status: The resulting HTTP status code.
    """
    __tablename__ = "authz_decisions"

    id = Column(String, primary_key=True)
    endpoint_url = Column(String, nullable=False, index=True)
    endpoint_method = Column(String, nullable=False)
    principal_id = Column(String, nullable=False, index=True)
    http_status = Column(String, nullable=False)
