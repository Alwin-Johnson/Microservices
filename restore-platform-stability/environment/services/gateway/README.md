# Gateway Service

The API Gateway is the single ingress point for the e-commerce platform. It routes incoming HTTP requests to the appropriate downstream service and returns responses to the caller.

---

## Responsibility

- Accept all inbound HTTP traffic on port **8000**.
- Route requests to Orders, Payments, and Inventory services.
- Return upstream responses to clients without modification.
- No business logic lives in this service.

---

## Port

| Service   | Port |
|-----------|------|
| `gateway` | 8000 |

---

## Upstream Services

| Service     | Docker hostname | Port |
|-------------|-----------------|------|
| `orders`    | `orders`        | 8001 |
| `payments`  | `payments`      | 8002 |
| `inventory` | `inventory`     | 8003 |

All upstream URLs are configured via environment variables. See the root [`.env.example`](../../.env.example).

---

## Structure

```
gateway/
├── app/              # FastAPI application
├── tests/            # Service tests
├── pyproject.toml    # Project and tooling configuration
├── requirements.txt  # Pinned dependencies
├── Dockerfile        # Service container definition
└── README.md         # This file
```

---

## Configuration

| Variable                | Default                     | Description                        |
|-------------------------|-----------------------------|------------------------------------|
| `GATEWAY_HOST`          | `0.0.0.0`                   | Bind host                          |
| `GATEWAY_PORT`          | `8000`                      | Bind port                          |
| `GATEWAY_LOG_LEVEL`     | `info`                      | Log level                          |
| `ORDERS_SERVICE_URL`    | `http://orders:8001`        | Orders service base URL            |
| `PAYMENTS_SERVICE_URL`  | `http://payments:8002`      | Payments service base URL          |
| `INVENTORY_SERVICE_URL` | `http://inventory:8003`     | Inventory service base URL         |

---

## Running Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Running Tests

```bash
pytest tests/
```
