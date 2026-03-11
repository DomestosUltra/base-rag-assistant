from fastapi import APIRouter
from starlette import status

from backend.schemas.common.responses import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
async def health() -> HealthResponse:
    """Проверить доступность backend сервиса.

    Returns:
        HealthResponse: Статус сервиса.
    """
    return HealthResponse(status="ok", service="bot-backend")
