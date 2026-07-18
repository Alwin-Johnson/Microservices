#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/../environment"

cat << 'EOF' > services/shared/db/dependencies.py
import time
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from shared.db.session import SessionLocal
from shared.logger.custom_logger import setup_logger

logger = setup_logger("db_transaction")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions."""
    if not SessionLocal:
        raise ValueError("DATABASE_URL is not configured in this environment.")

    start_time = time.perf_counter()
    logger.info("Database transaction started.")

    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
            duration = time.perf_counter() - start_time
            logger.info(
                "Database transaction committed.",
                extra={"extra_info": {"duration_s": round(duration, 4)}},
            )
        except BaseException as e:
            await session.rollback()
            duration = time.perf_counter() - start_time
            logger.error(
                "Database transaction failed and rolled back.",
                extra={
                    "extra_info": {"error": str(e), "duration_s": round(duration, 4)}
                },
            )
            raise
        finally:
            await session.close()

EOF

cat << 'EOF' > services/shared/clients/base.py
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

        # Retry only safe idempotent methods (never retry POST — it is not idempotent
        # and retrying would create duplicate orders / payments).
        _IDEMPOTENT = {"GET", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
        max_retries = 3 if method.upper() in _IDEMPOTENT else 1

        for attempt in range(max_retries):
            start_time = time.perf_counter()
            try:
                # Use the client's default timeout (which is aware of fault_mode)
                response = await self._client.request(
                    method, endpoint, headers=headers, **kwargs
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
                        # Bounded backoff: cap at 1 second to avoid request starvation
                        delay = min(0.5 * (2**attempt), 1.0) + random.uniform(0, 0.1)
                        await asyncio.sleep(delay)
                        continue  # Retry on server error (idempotent methods only)
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

                # Bounded backoff with jitter (capped at 1 second)
                delay = min(0.5 * (2**attempt), 1.0) + random.uniform(0, 0.1)
                await asyncio.sleep(delay)

    async def close(self):
        await self._client.aclose()

EOF

if command -v docker &> /dev/null && docker info &> /dev/null; then
    docker compose build gateway orders payments inventory || true
    docker compose up -d || true

    # Wait for postgres to be healthy before applying schema
    echo "Waiting for postgres..."
    for i in $(seq 1 30); do
        docker compose exec -T postgres pg_isready -U ecommerce_user -d ecommerce &>/dev/null && break
        sleep 2
    done

    # Apply schema and seed data
    echo "Applying database schema..."
    docker exec -i "$(docker ps --format '{{.Names}}' | grep postgres | head -1)" \
        psql -U ecommerce_user -d ecommerce < database/schema.sql || true
    docker exec -i "$(docker ps --format '{{.Names}}' | grep postgres | head -1)" \
        psql -U ecommerce_user -d ecommerce < database/seed.sql || true

    # Allow services time to detect schema and recover
    sleep 5
fi

