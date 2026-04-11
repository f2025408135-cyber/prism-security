"""Parallel HTTP execution engine."""

import asyncio
import structlog
from typing import Any

from prism.interfaces.http import IHTTPExecutor
from prism.http.client import AsyncHttpClient
from prism.http.request_builder import build_request
from prism.http.response import parse_response
from prism.http.storage import TrafficStorage
from prism.models.endpoint import Endpoint
from prism.models.principal import Principal
from prism.models.authz import AuthzDecision
from prism.exceptions import NetworkError, ScopeViolationError

logger = structlog.get_logger(__name__)


class HTTPExecutor(IHTTPExecutor):
    """Executes HTTP probes against authorized targets.

    This class coordinates the AsyncHttpClient, RateLimiter, RequestBuilder,
    and TrafficStorage to perform systematic API probing.
    """

    def __init__(self, client: AsyncHttpClient, storage: TrafficStorage) -> None:
        """Initialize the executor.

        Args:
            client: The configured AsyncHttpClient instance.
            storage: The TrafficStorage engine for recording traffic.
        """
        self.client = client
        self.storage = storage

    async def probe(
        self,
        endpoint: Endpoint,
        principal: Principal,
    ) -> AuthzDecision:
        """Send one probe. Return one decision. No side effects.

        Args:
            endpoint: The Endpoint to probe.
            principal: The Principal acting as the identity context.

        Returns:
            An AuthzDecision detailing what happened.
        """
        logger.debug("probe_execution_started", endpoint_url=endpoint.url, principal_id=principal.id)
        
        kwargs = build_request(endpoint, principal)
        method = kwargs.pop("method", "GET")
        url = kwargs.pop("url", "")
        
        status_code = 0
        timing_ms = 0.0
        is_authorized = False
        response_headers: tuple[tuple[str, str], ...] = ()
        body_excerpt = ""

        try:
            httpx_response, timing_ms = await self.client.request(method, url, **kwargs)
            parsed_resp = parse_response(httpx_response, timing_ms)
            
            status_code = parsed_resp.status_code
            response_headers = parsed_resp.headers
            body_excerpt = parsed_resp.body_excerpt
            is_authorized = (200 <= status_code < 300)
            
        except ScopeViolationError as e:
            logger.warning("probe_scope_violation", url=url, error=str(e))
            status_code = 403
            body_excerpt = str(e)
        except NetworkError as e:
            logger.error("probe_network_error", url=url, error=str(e))
            status_code = 0
            body_excerpt = str(e)

        # Store traffic for audit
        try:
            self.storage.store(
                principal_id=principal.id,
                request_kwargs={"method": method, "url": url, **kwargs},
                status_code=status_code,
                response_headers=response_headers,
                response_body=body_excerpt,
                timing_ms=timing_ms
            )
        except Exception as e:
            logger.warning("probe_storage_failed", url=url, error=str(e))

        decision = AuthzDecision(
            endpoint_url=endpoint.url,
            endpoint_method=endpoint.method,
            principal_id=principal.id,
            http_status=status_code,
            is_authorized=is_authorized,
            timing_ms=timing_ms
        )

        logger.info(
            "probe_execution_completed", 
            url=endpoint.url, 
            status=status_code, 
            is_authorized=is_authorized
        )
        return decision

    async def probe_concurrent(
        self,
        endpoint: Endpoint,
        principal: Principal,
        count: int,
        interval_ms: float = 0,
    ) -> list[AuthzDecision]:
        """Send N concurrent probes for race condition testing.

        Args:
            endpoint: The Endpoint to probe.
            principal: The Principal acting as the identity context.
            count: How many concurrent requests to send.
            interval_ms: The millisecond delay between dispatches (optional).

        Returns:
            A list of AuthzDecisions representing the parallel outcomes.
        """
        logger.info("probe_concurrent_started", count=count, url=endpoint.url)

        async def _delayed_probe(delay: float) -> AuthzDecision:
            if delay > 0:
                await asyncio.sleep(delay)
            return await self.probe(endpoint, principal)

        tasks = []
        for i in range(count):
            delay = (i * interval_ms) / 1000.0 if interval_ms > 0 else 0.0
            tasks.append(asyncio.create_task(_delayed_probe(delay)))

        results = await asyncio.gather(*tasks)
        logger.info("probe_concurrent_completed", count=len(results))
        return list(results)
