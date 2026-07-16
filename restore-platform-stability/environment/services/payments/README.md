# Payments Service

The Payments service processes payment transactions and maintains an authoritative record of all payment activity. It persists transaction state to PostgreSQL and uses Redis for idempotency key storage.

---

## Responsibility

- Process payment requests.
- Persist payment transaction records.
- Manage idempotency to prevent duplicate charges.
- No order management or inventory logic belongs in this service.

---

## Port

| Service    | Port |
|------------|------|
| `payments` | 8002 |

---

## Dependencies

| Dependency | Transport | Purpose                          |
|------------|-----------|----------------------------------|
| PostgreSQL | TCP       | Transaction persistence          |
| Redis      | TCP       | Idempotency key storage          |

---

## Structure

```
payments/
├── app/              # FastAPI application
├── tests/            # Service tests
├── pyproject.toml    # Project and tooling configuration
├── requirements.txt  # Pinned dependencies
├── Dockerfile        # Service container definition
└── README.md         # This file
```

---

## Configuration

| Variable             | Default              | Description                      |
|----------------------|----------------------|----------------------------------|
| `PAYMENTS_HOST`      | `0.0.0.0`            | Bind host                        |
| `PAYMENTS_PORT`      | `8002`               | Bind port                        |
| `PAYMENTS_LOG_LEVEL` | `info`               | Log level                        |
| `DATABASE_URL`       | —                    | PostgreSQL async DSN             |
| `REDIS_URL`          | `redis://redis:6379/0` | Redis connection URL            |

---

## Running Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

## Running Tests

```bash
pytest tests/
```
