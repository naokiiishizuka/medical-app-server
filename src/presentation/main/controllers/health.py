"""Controller for health-related endpoints."""

from src.presentation.main.generated import HealthRead200Response


class HealthController:
    """Coordinates health endpoint logic."""

    async def read_health(self) -> HealthRead200Response:
        """Produce a basic health response."""
        return HealthRead200Response(status="ok")
