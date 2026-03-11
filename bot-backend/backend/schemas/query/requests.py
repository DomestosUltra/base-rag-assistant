from pydantic import BaseModel, Field
from fastapi import Form


class TextImageRequest(BaseModel):
    """Запрос text/image endpoint для пользователя."""

    text: str = Field(min_length=1, description="Текстовый запрос")
    search_shared: bool = Field(default=True, description="Искать ли по общей базе знаний")

    @classmethod
    def as_form(
        cls,
        text: str = Form(...),
        search_shared: bool = Form(default=True),
    ) -> "TextImageRequest":
        """Создать DTO из multipart/form-data.

        Args:
            text: Текст запроса.
            search_shared: Флаг поиска по общей базе знаний.

        Returns:
            TextImageRequest: DTO запроса.
        """
        return cls(text=text, search_shared=search_shared)


class ClearMemoryRequest(BaseModel):
    """Запрос на очистку памяти диалога."""

    user_id: str = Field(min_length=1, max_length=128, description="Идентификатор пользователя")
