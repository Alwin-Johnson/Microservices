from fastapi import APIRouter, Depends, Request, Response, HTTPException
import httpx
import os

from shared.utils.http_client import get_http_client

router = APIRouter()

# URLs from environment or settings
ORDERS_URL = os.getenv("ORDERS_SERVICE_URL", "http://orders:8001")
PAYMENTS_URL = os.getenv("PAYMENTS_SERVICE_URL", "http://payments:8002")
INVENTORY_URL = os.getenv("INVENTORY_SERVICE_URL", "http://inventory:8003")


async def forward_request(
    url: str, request: Request, client: httpx.AsyncClient
) -> Response:
    try:
        body = await request.body()
        req = client.build_request(
            method=request.method,
            url=url,
            headers={
                k: v
                for k, v in request.headers.items()
                if k.lower() not in ("host", "content-length")
            },
            content=body,
        )
        response = await client.send(req)
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers={
                k: v
                for k, v in response.headers.items()
                if k.lower() not in ("content-encoding", "content-length")
            },
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Bad Gateway: {str(e)}")


@router.api_route(
    "/orders/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
@router.api_route("/orders", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_orders(
    request: Request,
    client: httpx.AsyncClient = Depends(get_http_client),
    path: str = "",
):
    target_path = f"/{path}" if path else ""
    return await forward_request(f"{ORDERS_URL}/orders{target_path}", request, client)


@router.api_route(
    "/payments/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
@router.api_route("/payments", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_payments(
    request: Request,
    client: httpx.AsyncClient = Depends(get_http_client),
    path: str = "",
):
    target_path = f"/{path}" if path else ""
    return await forward_request(
        f"{PAYMENTS_URL}/payments{target_path}", request, client
    )


@router.api_route(
    "/inventory/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
@router.api_route("/inventory", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_inventory(
    request: Request,
    client: httpx.AsyncClient = Depends(get_http_client),
    path: str = "",
):
    target_path = f"/{path}" if path else ""
    return await forward_request(
        f"{INVENTORY_URL}/inventory{target_path}", request, client
    )
