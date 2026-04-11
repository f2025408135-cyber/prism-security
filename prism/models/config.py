"""Configuration data models."""

from pydantic import BaseModel, ConfigDict, Field


class ScanConfig(BaseModel):
    """Configuration for a specific scan engagement.

    Attributes:
        target_url: The base URL of the target API.
        in_scope_patterns: Tuple of URL patterns explicitly in-scope.
        concurrency: Max number of parallel requests.
        rate_limit_per_second: Max requests per second.
    """
    model_config = ConfigDict(frozen=True)

    target_url: str
    in_scope_patterns: tuple[str, ...] = ()
    concurrency: int = 10
    rate_limit_per_second: float = 50.0


class Config(BaseModel):
    """Root configuration for PRISM framework.

    Attributes:
        workspace_dir: Directory where state and DB are stored.
        scan_config: The scan-specific configuration.
    """
    model_config = ConfigDict(frozen=True)

    workspace_dir: str = ".prism"
    scan_config: ScanConfig = Field(default_factory=lambda: ScanConfig(target_url=""))
