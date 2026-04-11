"""Endpoint and Request models representing API targets."""

from pydantic import BaseModel, ConfigDict


class Parameter(BaseModel):
    """Represents an HTTP request parameter.

    Attributes:
        name: The name of the parameter.
        value: The value of the parameter.
        location: Where the parameter is located ('query', 'header', 'path', 'body').
    """
    model_config = ConfigDict(frozen=True)

    name: str
    value: str
    location: str


class Endpoint(BaseModel):
    """Represents a single API endpoint target.

    Attributes:
        method: The HTTP method (e.g., 'GET', 'POST').
        url: The full URL of the endpoint.
        parameters: A tuple of predefined parameters for this endpoint.
    """
    model_config = ConfigDict(frozen=True)

    method: str
    url: str
    parameters: tuple[Parameter, ...] = ()


class Response(BaseModel):
    """Represents an HTTP response from an endpoint.

    Attributes:
        status_code: The HTTP status code.
        headers: A tuple of header key-value pairs.
        body_excerpt: A snippet of the response body for context.
        timing_ms: The time taken to receive the response in milliseconds.
    """
    model_config = ConfigDict(frozen=True)

    status_code: int
    headers: tuple[tuple[str, str], ...] = ()
    body_excerpt: str
    timing_ms: float
