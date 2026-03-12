from fastapi import Request
from fastapi.responses import JSONResponse

from backend.core.exceptions.base import CustomException


async def custom_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Преобразовать доменное исключение в HTTP ответ.

    Args:
        _: Объект запроса FastAPI.
        exc: Бизнес-исключение.

    Returns:
        JSONResponse: Сформированный HTTP ответ.
    """
    if isinstance(exc, CustomException):
        return JSONResponse(status_code=exc.status_code, content=exc.errors)
    return JSONResponse(status_code=500, content={"message": "Internal server error"})
