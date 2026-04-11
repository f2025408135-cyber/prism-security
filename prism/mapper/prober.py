"""Systematic endpoint × principal prober."""

import asyncio
import structlog

from prism.interfaces.http import IHTTPExecutor
from prism.models.endpoint import Endpoint
from prism.models.principal import Principal
from prism.models.authz import AuthzDecision

logger = structlog.get_logger(__name__)

# A profile is simply a tuple of decisions for a single endpoint across multiple principals
EndpointAuthzProfile = tuple[AuthzDecision, ...]


class EndpointProber:
    """Probes a single endpoint systematically across multiple authentication contexts."""

    def __init__(self, executor: IHTTPExecutor) -> None:
        """Initialize the prober.

        Args:
            executor: The HTTP executor to use for sending probes.
        """
        self.executor = executor

    async def map_endpoint(
        self,
        endpoint: Endpoint,
        principals: tuple[Principal, ...]
    ) -> EndpointAuthzProfile:
        """Probe an endpoint with all provided principals.

        This systematically sends a request to the endpoint using every principal
        context provided, gathering the authorization decisions.

        Args:
            endpoint: The Endpoint to probe.
            principals: A tuple of Principals to test access with.

        Returns:
            An EndpointAuthzProfile containing all decisions for this endpoint.
        """
        logger.info(
            "map_endpoint_started", 
            endpoint_url=endpoint.url, 
            principal_count=len(principals)
        )

        tasks = []
        for principal in principals:
            tasks.append(asyncio.create_task(self.executor.probe(endpoint, principal)))

        # Gather all probe results concurrently
        decisions: list[AuthzDecision] = await asyncio.gather(*tasks)

        logger.info(
            "map_endpoint_completed", 
            endpoint_url=endpoint.url, 
            decisions_recorded=len(decisions)
        )
        return tuple(decisions)
