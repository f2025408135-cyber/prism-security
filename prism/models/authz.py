"""Authorization decision and matrix models."""

from pydantic import BaseModel, ConfigDict


class AuthzDecision(BaseModel):
    """Represents the outcome of an authorization probe.

    Records what happened when a specific principal attempted to access
    a specific endpoint.

    Attributes:
        endpoint_url: The URL that was probed.
        endpoint_method: The HTTP method used.
        principal_id: The ID of the principal that attempted access.
        http_status: The HTTP status code returned.
        is_authorized: True if the request was successful (e.g. 2xx), False otherwise.
        timing_ms: How long the request took.
    """
    model_config = ConfigDict(frozen=True)

    endpoint_url: str
    endpoint_method: str
    principal_id: str
    http_status: int
    is_authorized: bool
    timing_ms: float


class AuthzMatrix(BaseModel):
    """Represents a mapping of endpoints and principals to decisions.

    Attributes:
        decisions: A tuple of all recorded authorization decisions.
    """
    model_config = ConfigDict(frozen=True)

    decisions: tuple[AuthzDecision, ...] = ()
