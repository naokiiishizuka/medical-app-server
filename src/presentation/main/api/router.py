"""Presentation layer root router factory."""

from fastapi import APIRouter

from src.presentation.main.api.routes import health


def create_api_router() -> APIRouter:
    """Aggregate all API routers exposed by the presentation layer."""
    router = APIRouter()
    router.include_router(health.router)
    return router
