# Inventory Service

The Inventory service manages product stock levels, stock reservations, and availability checks. It persists stock records to PostgreSQL and caches availability data in Redis to reduce database load.

---

## Responsibility

- Track product stock quantities.
- Reserve stock during order processing.
- Release reserved stock on cancellation.
- Expose stock availability for querying.
- No order or payment logic belongs in this service.

---

## Port

| Service     | Port |
|-------------|------|
| `inventory` | 8003 |

---

## Dependencies

| Dependency | Transport | Purpose                          |
|------------|-----------|----------------------------------|
| PostgreSQL | TCP       | Stock record persistence         |
| Redis      | TCP       | Availability cache               |

---

## Structure

```
inventory/
├── app/              # FastAPI application
├── tests/            # Service tests
├── pyproject.toml    # Project and tooling configuration
├── requirements.txt  # Pinned dependencies
├── Dockerfile        # Service container definition
└── README.md         # This file
```

---

## Configuration

| Variable              | Default                | Description                    |
|-----------------------|------------------------|--------------------------------|
| `INVENTORY_HOST`      | `0.0.0.0`              | Bind host                      |
| `INVENTORY_PORT`      | `8003`                 | Bind port                      |
| `INVENTORY_LOG_LEVEL` | `info`                 | Log level                      |
| `DATABASE_URL`        | —                      | PostgreSQL async DSN           |
| `REDIS_URL`           | `redis://redis:6379/0` | Redis connection URL           |

---

## Running Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

## Running Tests

```bash
pytest tests/
```
