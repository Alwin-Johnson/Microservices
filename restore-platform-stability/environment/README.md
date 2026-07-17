# restore-platform-stability

A production-grade distributed e-commerce platform built on a microservices architecture.


---

## Architecture

The platform consists of four independent FastAPI services backed by a shared PostgreSQL database, a shared Redis cache, and a shared infrastructure library.

```
┌────────────────────────────────────────────────────────┐
│                        Gateway                         │
│               (single ingress — port 8000)             │
└────────┬──────────────┬────────────────┬───────────────┘
         │              │                │
         ▼              ▼                ▼
    ┌─────────┐   ┌──────────┐   ┌───────────┐
    │  Orders │   │ Payments │   │ Inventory │
    │  :8001  │   │  :8002   │   │   :8003   │
    └────┬────┘   └────┬─────┘   └─────┬─────┘
         │              │               │
         └──────────────┴───────────────┘
                        │
              ┌─────────┴──────────┐
              │                    │
         ┌────▼─────┐       ┌──────▼───┐
         │PostgreSQL│       │  Redis   │
         │  :5432   │       │  :6379   │
         └──────────┘       └──────────┘
```

---

## Technology Stack

| Concern           | Technology                 | Version  |
|-------------------|----------------------------|----------|
| Language          | Python                     | 3.12     |
| Framework         | FastAPI                    | 0.115.6  |
| Database          | PostgreSQL                 | 16       |
| Cache             | Redis                      | 7        |
| ORM               | SQLAlchemy                 | 2.0.36   |
| DB Migrations     | Alembic                    | 1.14.0   |
| HTTP Client       | httpx                      | 0.28.1   |
| Configuration     | pydantic-settings          | 2.7.0    |
| Containerization  | Docker / Docker Compose    | —        |
| Testing           | pytest + pytest-asyncio    | 8.3.4    |

---

## Repository Structure

```
restore-platform-stability/
├── .env.example              # Environment variable reference
├── .gitignore
├── pyproject.toml            # Root tooling configuration
├── requirements.txt          # Developer tooling dependencies
├── Makefile                  # Developer convenience targets
├── docker-compose.yml        # Full-stack container orchestration
├── Dockerfile                # Base image definition
├── README.md                 # This file
│
├── configs/                  # Per-service runtime configuration files
│   ├── gateway.yaml
│   ├── orders.yaml
│   ├── payments.yaml
│   ├── inventory.yaml
│   ├── postgres.yaml
│   └── redis.yaml
│
├── database/                 # Database initialization
│   ├── schema.sql
│   ├── seed.sql
│   ├── init.sql
│   └── migrations/
│
├── monitoring/               # Observability configuration
├── workload/                 # Traffic replay tools
├── scripts/                  # Developer tooling scripts
│
└── services/
    ├── gateway/              # API Gateway service
    ├── orders/               # Orders service
    ├── payments/             # Payments service
    ├── inventory/            # Inventory service
    └── shared/               # Shared infrastructure library
```

---

## Services

| Service     | Port | Responsibility                                           |
|-------------|------|----------------------------------------------------------|
| `gateway`   | 8000 | Single ingress. Routes requests to downstream services.  |
| `orders`    | 8001 | Order lifecycle management and persistence.              |
| `payments`  | 8002 | Payment processing and transaction records.              |
| `inventory` | 8003 | Product stock management and availability checks.        |
| `shared`    | —    | Reusable infrastructure: DB, cache, config, logging.     |

---

## Getting Started

### Prerequisites

- Python 3.12
- Docker and Docker Compose
- `make` (optional, for convenience targets)

### Local Setup

**1. Clone the repository**

```bash
git clone <repository-url>
cd restore-platform-stability
```

**2. Configure environment variables**

```bash
cp .env.example .env
# Edit .env with appropriate values for your local environment
```

**3. Install developer tooling**

```bash
pip install -r requirements.txt
```

**4. Install a specific service for local development**

```bash
cd services/orders
pip install -r requirements.txt
```

**5. Start the full stack**

```bash
docker compose up --build
```

---

## Service-to-Service Communication

Services communicate over HTTP using Docker service names as hostnames. `localhost` is never used for inter-container communication.

| From        | To          | Base URL                     |
|-------------|-------------|------------------------------|
| `gateway`   | `orders`    | `http://orders:8001`         |
| `gateway`   | `payments`  | `http://payments:8002`       |
| `gateway`   | `inventory` | `http://inventory:8003`      |
| `orders`    | `payments`  | `http://payments:8002`       |
| `orders`    | `inventory` | `http://inventory:8003`      |

All service base URLs are configured via environment variables. See [`.env.example`](.env.example).

---

## Development Principles

- **Production quality**: Every implementation reflects real production engineering practices.
- **Type hints**: All public functions must carry type annotations.
- **PEP 8**: Code style enforced by `ruff`.
- **No hardcoded values**: All configuration is sourced from environment variables.
- **Low coupling**: Services are independently deployable.
- **No shared business logic**: The `shared` library contains only infrastructure concerns.

---

## Running Tests

```bash
# Run all tests
pytest

# Run tests for a specific service
pytest services/orders/tests/

# Run with coverage
pytest --cov=services/orders/app services/orders/tests/
```

---

## Code Quality

```bash
# Lint
ruff check .

# Format
ruff format .

# Type-check
mypy services/
```
