# Shared Infrastructure Library

The `shared` library provides reusable infrastructure components consumed by all platform services. It contains no business logic.

---

## Responsibility

Provide production-ready, reusable building blocks for:

- Database connectivity (SQLAlchemy async engine and session management)
- Redis cache client
- Configuration base classes (pydantic-settings)
- Structured logging setup
- Common HTTP utilities
- Shared exception types and error response models

**This library must never import from or depend on any individual service (`orders`, `payments`, `inventory`, `gateway`).**

---

## What Does Not Belong Here

- Order processing logic
- Payment processing logic
- Inventory management logic
- Routing or endpoint definitions
- Business rules of any kind

---

## Structure

```
shared/
├── config/           # Base settings and configuration utilities
├── db/               # Database engine, session factory, base model
├── redis/            # Redis client factory
├── logger/           # Logging configuration
├── errors/           # Common exception types and HTTP error responses
├── middleware/        # Reusable ASGI middleware
├── models/           # Shared SQLAlchemy base and mixins
├── constants/        # Platform-wide constants
├── utils/            # General-purpose utilities
├── validation/       # Common validators
├── response/         # Standard API response envelope types
├── tracing/          # (Reserved) Distributed tracing integration point
├── metrics/          # (Reserved) Metrics integration point
├── pyproject.toml    # Project and tooling configuration
├── requirements.txt  # Pinned dependencies
└── README.md         # This file
```

---

## Installation

The shared library is installed as an editable local package by each service:

```
# In each service's requirements.txt
-e ../shared
```

---

## Usage Convention

Services import from the `shared` package namespace:

```python
from shared.db import get_session
from shared.config import BaseServiceSettings
from shared.logger import configure_logging
```

---

## Dependencies

| Package          | Version  | Purpose                          |
|------------------|----------|----------------------------------|
| fastapi          | 0.115.6  | ASGI framework primitives        |
| sqlalchemy       | 2.0.36   | ORM and async session management |
| alembic          | 1.14.0   | Database migrations              |
| asyncpg          | 0.30.0   | Async PostgreSQL driver          |
| redis            | 5.2.1    | Redis client                     |
| httpx            | 0.28.1   | Async HTTP client                |
| pydantic         | 2.10.4   | Data validation                  |
| pydantic-settings| 2.7.0    | Environment-based configuration  |
