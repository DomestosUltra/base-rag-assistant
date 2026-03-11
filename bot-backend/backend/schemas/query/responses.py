from pydantic import BaseModel, Field


class QueryResponse(BaseModel):
    """Ответ на запрос к консультанту."""

    answer: str = Field(description="Ответ ассистента")


class ClearMemoryResponse(BaseModel):
    """Ответ на очистку памяти пользователя."""

    cleared: bool = Field(description="Была ли память очищена")
