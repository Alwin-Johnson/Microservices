from typing import List, Dict, Any
from shared.clients.services import OrdersClient, PaymentsClient, InventoryClient
from shared.errors.exceptions import PlatformError, ValidationError

class CheckoutService:
    def __init__(self):
        self.orders_client = OrdersClient()
        self.payments_client = PaymentsClient()
        self.inventory_client = InventoryClient()

    async def execute_checkout(self, customer_id: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not items:
            raise ValidationError("Checkout requires at least one item.")

        total_amount = 0.0
        # Calculate total amount by fetching item prices
        try:
            for item in items:
                inventory_item = await self.inventory_client.get_inventory(item["sku"])
                total_amount += float(inventory_item["price"]) * item["quantity"]
        except Exception as e:
            if isinstance(e, PlatformError):
                raise e
            raise PlatformError(status_code=400, detail=f"Failed to calculate total amount: {str(e)}")
            
        # Step 1: Create Order (Status: PENDING)
        try:
            order = await self.orders_client.create_order(customer_id, total_amount)
            order_id = order["id"]
        except Exception as e:
            raise PlatformError(status_code=500, detail=f"Failed to create order: {str(e)}")

        successful_reservations = []

        try:
            # Step 2: Reserve Inventory
            for item in items:
                reservation = await self.inventory_client.reserve_inventory(
                    order_id=order_id,
                    sku=item["sku"],
                    quantity=item["quantity"]
                )
                successful_reservations.append(reservation["id"])

            # Step 3: Process Payment
            # Assuming the order response contains the dynamically calculated total_amount
            payment_amount = order["total_amount"]
            await self.payments_client.process_payment(order_id=order_id, amount=payment_amount)

            # Step 4: Complete Order
            completed_order = await self.orders_client.complete_order(order_id)
            return completed_order

        except Exception as e:
            # Rollback logic
            for res_id in successful_reservations:
                try:
                    await self.inventory_client.release_inventory(res_id)
                except Exception:
                    # Best effort rollback, log the failure in real life
                    pass

            try:
                await self.orders_client.fail_order(order_id)
            except Exception:
                pass

            # Raise a mapped error that proxy can understand
            if isinstance(e, PlatformError):
                raise e
            raise PlatformError(status_code=400, detail=f"Checkout failed: {str(e)}")
