import httpx
from typing import Any, Dict, Optional
from shared.errors.exceptions import PlatformError, ServiceUnavailableError

class BaseHttpClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        # We reuse the client per instance, but for simple use cases httpx.AsyncClient is created per request or bound
        self._client = httpx.AsyncClient(base_url=self.base_url)

    async def get(self, endpoint: str) -> Dict[str, Any]:
        return await self._request("GET", endpoint)

    async def post(self, endpoint: str, json: Dict[str, Any] = None) -> Dict[str, Any]:
        return await self._request("POST", endpoint, json=json)
        
    async def put(self, endpoint: str, json: Dict[str, Any] = None) -> Dict[str, Any]:
        return await self._request("PUT", endpoint, json=json)
        
    async def patch(self, endpoint: str, json: Dict[str, Any] = None) -> Dict[str, Any]:
        return await self._request("PATCH", endpoint, json=json)
        
    async def delete(self, endpoint: str) -> None:
        await self._request("DELETE", endpoint)

    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        try:
            response = await self._client.request(method, endpoint, **kwargs)
            if response.status_code >= 400:
                # Handle standard HTTP errors gracefully by raising PlatformError
                # so the downstream router can return the correct status.
                detail = response.text
                try:
                    data = response.json()
                    detail = data.get("detail", detail)
                except Exception:
                    pass
                raise PlatformError(status_code=response.status_code, detail=detail)
            
            # For 204 No Content
            if response.status_code == 204:
                return None
                
            return response.json()
        except httpx.RequestError as e:
            raise ServiceUnavailableError(f"Error communicating with service: {str(e)}")

    async def close(self):
        await self._client.aclose()
