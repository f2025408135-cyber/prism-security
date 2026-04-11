"""Custom exception classes for the PRISM framework."""

class PrismError(Exception):
    """Base exception for all custom PRISM exceptions."""
    pass


class ConfigurationError(PrismError):
    """Raised when there is an invalid configuration."""
    pass


class ScopeViolationError(PrismError):
    """Raised when an attempt is made to access an out-of-scope URL."""
    pass


class NetworkError(PrismError):
    """Raised when an HTTP operation fails due to connectivity issues."""
    pass


class IngestionError(PrismError):
    """Raised when parsing a target API spec fails."""
    pass


class StorageError(PrismError):
    """Raised when a database operation fails."""
    pass
