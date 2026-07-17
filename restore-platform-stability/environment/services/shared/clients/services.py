from typing import Any, Dict, List
from shared.clients.base import BaseHttpClient
from shared.config.settings import settings


class OrdersClient(BaseHttpClient):
    def __init__(self):
        super().__init__(settings.orders_service_url)

    async def create_order(
        self, customer_id: str, total_amount: float
    ) -> Dict[str, Any]:
        return await self.post(
            "/orders", json={"customer_id": customer_id, "total_amount": total_amount}
        )

    async def get_order(self, order_id: str) -> Dict[str, Any]:
        return await self.get(f"/orders/{order_id}")

    async def list_orders(self, customer_id: str) -> List[Dict[str, Any]]:
        return await self.get(f"/orders/customer/{customer_id}")

    async def complete_order(self, order_id: str) -> Dict[str, Any]:
        return await self.patch(f"/orders/{order_id}/complete")

    async def fail_order(self, order_id: str) -> Dict[str, Any]:
        return await self.patch(f"/orders/{order_id}/fail")


class PaymentsClient(BaseHttpClient):
    def __init__(self):
        super().__init__(settings.payments_service_url)

    async def process_payment(self, order_id: str, amount: float) -> Dict[str, Any]:
        return await self.post(
            "/payments", json={"order_id": order_id, "amount": amount}
        )

    async def get_payment(self, payment_id: str) -> Dict[str, Any]:
        return await self.get(f"/payments/{payment_id}")


class InventoryClient(BaseHttpClient):
    def __init__(self):
        super().__init__(settings.inventory_service_url)

    async def reserve_inventory(
        self, order_id: str, sku: str, quantity: int
    ) -> Dict[str, Any]:
        return await self.post(
            "/inventory/reserve",
            json={"order_id": order_id, "sku": sku, "quantity": quantity},
        )

    async def release_inventory(self, reservation_id: str) -> None:
        await self.post(f"/inventory/release/{reservation_id}")

    async def get_inventory(self, sku: str) -> Dict[str, Any]:
        return await self.get(f"/inventory/{sku}")
