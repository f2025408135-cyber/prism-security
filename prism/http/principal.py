"""Authentication context management."""

import uuid
import structlog
from typing import Any

from prism.models.principal import Principal, Token, Credential
from prism.exceptions import ConfigurationError

logger = structlog.get_logger(__name__)


class PrincipalManager:
    """Manages authentication contexts and tokens for different roles.

    This class keeps track of all active principals (e.g. admin, user_a,
    user_b, anonymous) and their associated active tokens.
    """

    def __init__(self) -> None:
        """Initialize the PrincipalManager."""
        self._principals: dict[str, Principal] = {}
        self._tokens: dict[str, Token] = {}
        
        # Always initialize an anonymous principal by default
        self._create_anonymous()

    def _create_anonymous(self) -> None:
        """Create the default anonymous principal with no tokens."""
        anon = Principal(id="anonymous_1", name="anonymous")
        self._principals[anon.id] = anon
        logger.debug("anonymous_principal_initialized", id=anon.id)

    def register_principal(self, name: str, roles: tuple[str, ...]) -> Principal:
        """Register a new principal in the system.

        Args:
            name: Human-readable name.
            roles: A tuple of role strings.

        Returns:
            The created frozen Principal model.
        """
        principal = Principal(
            id=str(uuid.uuid4()),
            name=name,
            roles=frozenset(roles)
        )
        self._principals[principal.id] = principal
        logger.info("principal_registered", id=principal.id, name=name, roles=list(roles))
        return principal

    def add_token(self, principal_id: str, token_value: str, token_type: str = "Bearer") -> Token:
        """Associate an authentication token with a principal.

        Args:
            principal_id: The ID of the principal.
            token_value: The sensitive token string.
            token_type: The type (e.g. Bearer, API-Key).

        Returns:
            The created frozen Token model.

        Raises:
            ConfigurationError: If the principal_id is not registered.
        """
        if principal_id not in self._principals:
            raise ConfigurationError(f"Principal {principal_id} not found.")

        token = Token(
            principal_id=principal_id,
            value=token_value,
            token_type=token_type
        )
        self._tokens[principal_id] = token
        
        # Secure logging: only log first 8 chars of token
        safe_token = token_value[:8] + "..." if len(token_value) > 8 else "***"
        logger.info(
            "token_added", 
            principal_id=principal_id, 
            token_type=token_type, 
            token_preview=safe_token
        )
        return token

    def get_token(self, principal_id: str) -> Token | None:
        """Retrieve the active token for a given principal.

        Args:
            principal_id: The ID of the principal.

        Returns:
            The Token model if one exists, else None.
        """
        return self._tokens.get(principal_id)

    def get_all_principals(self) -> list[Principal]:
        """Retrieve all registered principals, including anonymous.

        Returns:
            A list of Principal models.
        """
        return list(self._principals.values())
