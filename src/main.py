"""Application entrypoint wiring the Clean Architecture layers."""

import os

import uvicorn
from fastapi import FastAPI

from src.presentation.main.api import create_api_router


def create_app() -> FastAPI:
    """Build and return the FastAPI application instance."""
    app = FastAPI(title="Medical App Server", version="0.1.0")
    app.include_router(create_api_router())
    return app


def main() -> None:
    """Entrypoint for running the service via `python -m src.main`."""
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    uvicorn.run("src.main:create_app", host=host, port=port, factory=True)


if __name__ == "__main__":
    main()
