"""Application entrypoint wiring the Clean Architecture layers."""

import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.infrastructure.main.db.session import dispose_engine, get_engine
from src.presentation.main.api import create_api_router


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: D401
    """Initialize resources on startup and dispose them at shutdown."""
    get_engine()
    try:
        yield
    finally:
        await dispose_engine()


def create_app() -> FastAPI:
    """Build and return the FastAPI application instance."""
    app = FastAPI(title="Medical App Server", version="0.1.0", lifespan=lifespan)
    app.include_router(create_api_router())
    return app


def main() -> None:
    """Entrypoint for running the service via `python -m src.main`."""
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    uvicorn.run("src.main:create_app", host=host, port=port, factory=True)


if __name__ == "__main__":
    main()
