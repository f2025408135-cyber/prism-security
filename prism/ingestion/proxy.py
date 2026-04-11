"""Live traffic capture using mitmproxy."""

import asyncio
import structlog
from urllib.parse import urlparse

# mitmproxy imports
from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.http import HTTPFlow

from prism.models.endpoint import Endpoint, Parameter
from prism.exceptions import IngestionError

logger = structlog.get_logger(__name__)


class PrismMitmAddon:
    """Mitmproxy addon that intercepts flows and converts them to Endpoints."""

    def __init__(self, target_host: str):
        self.target_host = target_host
        self.endpoints: set[Endpoint] = set()
        self.seen_signatures: set[str] = set()

    def request(self, flow: HTTPFlow) -> None:
        """Process an intercepted HTTP request.
        
        Extracts the method, URL, and parameters if it matches the target host.
        """
        if not flow.request.host == self.target_host:
            return

        method = flow.request.method.upper()
        if method not in ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]:
            return

        url = flow.request.url

        # Deduplication signature
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        signature = f"{method}:{base_url}"
        
        if signature in self.seen_signatures:
            return
            
        self.seen_signatures.add(signature)

        extracted_params: list[Parameter] = []

        # Query parameters
        for key, value in flow.request.query.items():
            extracted_params.append(
                Parameter(name=key, value=value, location="query")
            )

        # Non-standard headers
        for key, value in flow.request.headers.items():
            if key.lower() not in ["accept", "user-agent", "host", "connection", "accept-encoding"]:
                extracted_params.append(
                    Parameter(name=key, value=value, location="header")
                )

        endpoint = Endpoint(
            method=method,
            url=url,
            parameters=tuple(extracted_params)
        )
        self.endpoints.add(endpoint)


async def run_proxy_capture(target_host: str, port: int = 8080, timeout_seconds: float = 60.0) -> tuple[Endpoint, ...]:
    """Run an embedded mitmproxy instance to capture live traffic.

    Args:
        target_host: The domain to capture traffic for (e.g., 'api.example.com').
        port: The local port to run the proxy on.
        timeout_seconds: How long to run the proxy before stopping.

    Returns:
        A tuple of extracted, frozen Endpoint models.

    Raises:
        IngestionError: If the proxy fails to start.
    """
    logger.info("proxy_capture_started", target_host=target_host, port=port, timeout=timeout_seconds)

    addon = PrismMitmAddon(target_host)
    opts = options.Options(listen_host='127.0.0.1', listen_port=port)

    try:
        m = DumpMaster(opts, with_termlog=False, with_dumper=False)
        m.addons.add(addon)
    except Exception as e:
        logger.error("proxy_initialization_failed", error=str(e))
        raise IngestionError(f"Failed to initialize mitmproxy: {e}") from e

    async def proxy_runner() -> None:
        try:
            await m.run()
        except asyncio.CancelledError:
            m.shutdown()

    proxy_task = asyncio.create_task(proxy_runner())

    try:
        await asyncio.sleep(timeout_seconds)
    finally:
        proxy_task.cancel()
        try:
            await proxy_task
        except asyncio.CancelledError:
            pass

    logger.info("proxy_capture_completed", endpoint_count=len(addon.endpoints))
    return tuple(addon.endpoints)
