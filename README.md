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
│   │   └── generated/   # Auto-generated code from OpenAPI specs
│   └── test/
├── openapi/             # API contract
│   └── openapi.yaml     # Source OpenAPI definition
├── shared/              # Cross-cutting concerns (config, utils)
│   ├── main/
│   │   ├── config/
│   │   └── utils/
│   └── test/
└── main.py              # Application entrypoint / composition root
```

> Add new modules within the appropriate layer and depend only on the layer directly beneath it (presentation → application → domain). Infrastructure provides implementations for application interfaces. Place layer-specific unit tests under each `src/<layer>/test` directory; use `tests/` for cross-layer or end-to-end scenarios.

## OpenAPI-driven interface generation

1. Maintain the canonical API contract in `src/openapi/openapi.yaml`.
2. Run `./scripts/generate_presentation.sh` to regenerate presentation-layer interface stubs. The script prefers a locally installed `openapi-generator-cli` but transparently falls back to Docker (`openapitools/openapi-generator-cli`) when available; override the image with `DOCKER_IMAGE`.
3. The script first wipes any previously generated files, then regenerates only OpenAPI-driven models (default `--global-property models`). Output is flattened so the usable artifacts end up under `src/presentation/main/generated/src/models/` (configurable via `GENERATED_PACKAGE`). Generated tests are removed by default (`STRIP_TESTS=true`) to avoid clutter. Copy or adapt the needed files manually into `src/presentation/main/api` etc., and tweak the `GLOBAL_PROPERTIES` env var if you need additional artifacts (e.g., add `apis` to generate route stubs and integrate them manually).

## Local development

1. Create a virtual environment (e.g., `python -m venv .venv && source .venv/bin/activate`).
2. Install dependencies: `pip install -e .[dev]`.
3. Run the API with live reload: `uvicorn src.main:create_app --factory --host 0.0.0.0 --port 8000 --reload`.
4. Visit `http://localhost:8000/docs` for the interactive Swagger UI generated from the FastAPI app.

The default host/port can also be controlled via the `APP_HOST` and `APP_PORT` environment variables when invoking `python -m src.main`.

## Docker

Build and run via Docker Compose (recommended for parity with production):

```bash
docker compose up --build
```

This maps port `8000` on the host to the container. To build and run manually:

```bash
docker build -t medical-app-server .
docker run --rm -p 8000:8000 medical-app-server
```
