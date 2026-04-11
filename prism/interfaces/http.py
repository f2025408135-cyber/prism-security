"""HTTP execution engine interfaces."""

from typing import Protocol, runtime_checkable

from prism.models.endpoint import Endpoint
from prism.models.principal import Principal
from prism.models.authz import AuthzDecision


class IHTTPExecutor(Protocol):
    """Executes HTTP probes against authorized targets."""

    async def probe(
        self,
        endpoint: Endpoint,
        principal: Principal,
    ) -> AuthzDecision:
        """Send one probe. Return one decision. No side effects."""
        ...

    async def probe_concurrent(
        self,
        endpoint: Endpoint,
        principal: Principal,
        count: int,
        interval_ms: float = 0,
    ) -> list[AuthzDecision]:
        """Send N concurrent probes for race condition testing."""
        ...


@runtime_checkable
class IScopeGuard(Protocol):
    """Enforces scope boundaries. Safety-critical."""

    def is_in_scope(self, url: str) -> bool:
        """Return True only if URL is explicitly in-scope."""
        ...

    def add_scope(self, pattern: str) -> None:
        """Add a URL pattern to the in-scope list."""
        ...
