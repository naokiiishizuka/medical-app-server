# medical-app-server

Python Web API server structured with Domain-Driven Design (DDD) and Clean Architecture principles. The repository currently exposes a directory skeleton so features can be implemented without breaking the architectural boundaries.

```
src/
├── application/         # Use cases orchestrating domain logic
│   ├── main/            # Production code for the application layer
│   │   ├── dto/         # Request/response DTO definitions
│   │   ├── interfaces/  # Ports describing interactions with outer layers
│   │   └── use_cases/   # Application services / interactors
│   └── test/            # Layer-specific tests
├── domain/              # Pure domain model
│   ├── main/
│   │   ├── entities/
│   │   ├── events/
│   │   ├── repositories/    # Abstract repository contracts
│   │   ├── services/        # Domain services
│   │   └── value_objects/
│   └── test/
├── infrastructure/      # Framework & IO adapters (DB, messaging, etc.)
│   ├── main/
│   │   ├── db/
│   │   ├── http/
│   │   ├── messaging/
│   │   └── repositories/    # Concrete repository implementations
│   └── test/
├── presentation/        # Interface adapters (e.g., Web API controllers)
│   ├── main/
│   │   ├── api/
│   │   ├── dependencies/
│   │   └── schemas/
│   └── test/
├── shared/              # Cross-cutting concerns (config, utils)
│   ├── main/
│   │   ├── config/
│   │   └── utils/
│   └── test/
└── main.py              # Application entrypoint / composition root
```

> Add new modules within the appropriate layer and depend only on the layer directly beneath it (presentation → application → domain). Infrastructure provides implementations for application interfaces. Place layer-specific unit tests under each `src/<layer>/test` directory; use `tests/` for cross-layer or end-to-end scenarios.
