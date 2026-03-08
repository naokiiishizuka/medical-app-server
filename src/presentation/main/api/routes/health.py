"""Health check endpoint."""

from fastapi import APIRouter, Depends

from src.presentation.main.controllers import HealthController
from src.presentation.main.generated import HealthRead200Response

router = APIRouter(prefix="/health", tags=["health"])


def get_health_controller() -> HealthController:
    """Dependency wire-up for HealthController."""
    return HealthController()


@router.get("", response_model=HealthRead200Response)
async def read_health(
    controller: HealthController = Depends(get_health_controller),
) -> HealthRead200Response:
    """Return service health metadata."""
    return await controller.read_health()
