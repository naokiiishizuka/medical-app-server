"""Application entrypoint wiring the Clean Architecture layers."""

from typing import Any


def create_app() -> Any:
    """Build and return the framework-specific application instance."""
    raise NotImplementedError("Provide wiring logic for presentation/application layers")


def main() -> None:
    """Entrypoint for running the service via `python -m src.main`."""
    create_app()


if __name__ == "__main__":
    main()
