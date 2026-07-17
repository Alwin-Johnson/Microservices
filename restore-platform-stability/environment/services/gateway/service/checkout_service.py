import time
from typing import Dict, Any, List
from shared.clients.services import OrdersClient, PaymentsClient, InventoryClient
from shared.errors.exceptions import PlatformError
from shared.metrics.prometheus import CHECKOUT_LATENCY


class CheckoutService:
    def __init__(self):
        self.orders_client = OrdersClient()
        self.payments_client = PaymentsClient()
        self.inventory_client = InventoryClient()

    async def execute_checkout(
        self, customer_id: str, items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Orchestrates the distributed checkout saga.
        Returns the final order state or raises an exception.
        """
        from shared.errors.exceptions import ValidationError

        if not items:
            raise ValidationError("Checkout requires at least one item.")

        start_time = time.perf_counter()

        total_amount = 0.0
        # Calculate total amount by fetching item prices
        try:
            for item in items:
                inventory_item = await self.inventory_client.get_inventory(item["sku"])
                total_amount += float(inventory_item["price"]) * item["quantity"]
        except Exception as e:
            if isinstance(e, PlatformError):
                raise e
            raise PlatformError(
                status_code=400, detail=f"Failed to calculate total amount: {str(e)}"
            )

        # Step 1: Create Order (Status: PENDING)
        order = await self.orders_client.create_order(customer_id, total_amount)
        order_id = order["id"]

        reservations = []
        try:
            # Step 2: Reserve Inventory
            for item in items:
                res = await self.inventory_client.reserve_inventory(
                    order_id=order_id, sku=item["sku"], quantity=item["quantity"]
                )
                reservations.append(res)

            # Step 3: Process Payment
            await self.payments_client.process_payment(
                order_id=order_id, amount=total_amount
            )

            # Step 4: Complete Order
            completed_order = await self.orders_client.complete_order(order_id)

            # Record success metric
            CHECKOUT_LATENCY.observe(time.perf_counter() - start_time)

            return completed_order

        except Exception as e:
            # Saga Rollback
            # 1. Release reserved inventory
            for res in reservations:
                try:
                    await self.inventory_client.release_inventory(res["id"])
                except Exception:
                    pass
            # 2. Mark order as failed
            try:
                await self.orders_client.fail_order(order_id)
            except Exception:
                pass

            if isinstance(e, PlatformError):
                raise e
            raise PlatformError(
                status_code=500, detail=f"Checkout workflow failed: {str(e)}"
            )
