import time
import random
import asyncio
from typing import Any, Dict
import httpx
from shared.errors.exceptions import PlatformError, ServiceUnavailableError
from shared.logger.context import get_correlation_id
from shared.logger.custom_logger import setup_logger
from shared.metrics.prometheus import OUTBOUND_REQUEST_COUNT, OUTBOUND_REQUEST_LATENCY

logger = setup_logger("http_client")


class BaseHttpClient:
    def __init__(self, base_url: str):
        from shared.config.settings import settings

        self.base_url = base_url.rstrip("/")
        timeout = 30.0 if settings.fault_mode == "on" else 5.0
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    async def get(self, endpoint: str) -> Dict[str, Any]:
        return await self._request("GET", endpoint)

    async def post(self, endpoint: str, json: Dict[str, Any] = None) -> Dict[str, Any]:
        return await self._request("POST", endpoint, json=json)

    async def put(self, endpoint: str, json: Dict[str, Any] = None) -> Dict[str, Any]:
        return await self._request("PUT", endpoint, json=json)

    async def patch(self, endpoint: str, json: Dict[str, Any] = None) -> Dict[str, Any]:
        return await self._request("PATCH", endpoint, json=json)

    async def delete(self, endpoint: str) -> None:
        return await self._request("DELETE", endpoint)

    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        headers = kwargs.pop("headers", {})
        correlation_id = get_correlation_id()
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        url = f"{self.base_url}{endpoint}"

        # Ensure high availability via retry policies
        max_retries = 6
        for attempt in range(max_retries):
            start_time = time.perf_counter()
            try:
                # Fail fast to prevent cascading blocks
                response = await self._client.request(
                    method, endpoint, headers=headers, timeout=2.0, **kwargs
                )
                duration = time.perf_counter() - start_time

                # Record metrics
                OUTBOUND_REQUEST_COUNT.labels(
                    method=method,
                    target_url=self.base_url,
                    status_code=str(response.status_code),
                ).inc()
                OUTBOUND_REQUEST_LATENCY.labels(
                    method=method, target_url=self.base_url
                ).observe(duration)

                if response.status_code >= 500:
                    if attempt < max_retries - 1:
                        continue  # Retry on server error
                    raise PlatformError(
                        status_code=response.status_code, detail=response.text
                    )

                if response.status_code >= 400:
                    detail = response.text
                    try:
                        data = response.json()
                        detail = data.get("detail", detail)
                    except Exception:
                        pass
                    raise PlatformError(status_code=response.status_code, detail=detail)

                if response.status_code == 204:
                    return None

                return response.json()

            except (httpx.RequestError, httpx.TimeoutException) as e:
                duration = time.perf_counter() - start_time

                OUTBOUND_REQUEST_COUNT.labels(
                    method=method, target_url=self.base_url, status_code="500"
                ).inc()
                OUTBOUND_REQUEST_LATENCY.labels(
                    method=method, target_url=self.base_url
                ).observe(duration)

                if attempt == max_retries - 1:
                    logger.error(
                        f"Outbound request failed: {method} {url}",
                        extra={
                            "extra_info": {
                                "method": method,
                                "url": url,
                                "error": str(e),
                                "duration_s": round(duration, 4),
                            }
                        },
                        exc_info=True,
                    )
                    raise ServiceUnavailableError(
                        f"Error communicating with service: {str(e)}"
                    )

                continue

    async def close(self):
        await self._client.aclose()
