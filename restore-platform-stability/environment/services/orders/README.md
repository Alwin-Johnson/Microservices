# Orders Service

The Orders service manages the full lifecycle of customer orders: creation, status tracking, and persistent storage. It coordinates with the Payments and Inventory services over HTTP.

---

## Responsibility

- Create and persist orders.
- Track order status transitions.
- Communicate with Payments and Inventory services as part of order processing.
- No payment logic or stock management belongs in this service.

---

## Port

| Service  | Port |
|----------|------|
| `orders` | 8001 |

---

## Dependencies

| Dependency  | Transport | Purpose                          |
|-------------|-----------|----------------------------------|
| PostgreSQL  | TCP       | Order persistence                |
| `payments`  | HTTP      | Payment coordination             |
| `inventory` | HTTP      | Stock reservation                |

---

## Structure

```
orders/
├── app/              # FastAPI application
├── tests/            # Service tests
├── pyproject.toml    # Project and tooling configuration
├── requirements.txt  # Pinned dependencies
├── Dockerfile        # Service container definition
└── README.md         # This file
```

---

## Configuration

| Variable                | Default                    | Description                       |
|-------------------------|----------------------------|-----------------------------------|
| `ORDERS_HOST`           | `0.0.0.0`                  | Bind host                         |
| `ORDERS_PORT`           | `8001`                     | Bind port                         |
| `ORDERS_LOG_LEVEL`      | `info`                     | Log level                         |
| `DATABASE_URL`          | —                          | PostgreSQL async DSN              |
| `PAYMENTS_SERVICE_URL`  | `http://payments:8002`     | Payments service base URL         |
| `INVENTORY_SERVICE_URL` | `http://inventory:8003`    | Inventory service base URL        |

---

## Running Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## Running Tests

```bash
pytest tests/
```
