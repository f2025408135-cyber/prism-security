"""Principal models representing authentication contexts."""

import uuid
from pydantic import BaseModel, ConfigDict, Field


class Principal(BaseModel):
    """Represents a unique user or service authentication context.

    A principal encapsulates the credentials needed to make authenticated
    requests on behalf of a specific identity.

    Attributes:
        id: Unique internal identifier for this principal.
        name: Human-readable name (e.g., 'admin_user', 'tenant_a').
        roles: Immutable set of role names associated with this principal.
    """
    model_config = ConfigDict(frozen=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    roles: frozenset[str] = frozenset()


class Token(BaseModel):
    """Represents an authentication token (e.g., JWT, Bearer).

    Tokens are associated with a Principal. The actual token value must
    never be logged in plain text.

    Attributes:
        principal_id: The ID of the principal this token belongs to.
        value: The actual token string.
        token_type: The type of token (e.g., 'Bearer', 'API-Key').
    """
    model_config = ConfigDict(frozen=True)

    principal_id: str
    value: str
    token_type: str = "Bearer"


class Credential(BaseModel):
    """Represents login credentials (e.g., username/password).

    Attributes:
        principal_id: The ID of the principal these credentials belong to.
        username: The username or email.
        password: The password (must not be logged).
    """
    model_config = ConfigDict(frozen=True)

    principal_id: str
    username: str
    password: str
