from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Модель ответа health-check."""

    status: str = Field(description="Статус сервиса")
    service: str = Field(description="Имя сервиса")


class ErrorResponse(BaseModel):
    """Модель ответа ошибки."""

    message: str = Field(description="Сообщение об ошибке")
    messageEn: str = Field(description="Сообщение об ошибке на английском")
