from pydantic import BaseModel, Field


class DialogueCreateRequest(BaseModel):
    """DTO запроса для сохранения записи диалога."""

    user_id: str = Field(min_length=1, max_length=128, description="Идентификатор пользователя")
    request_text: str = Field(min_length=1, description="Текст запроса пользователя")
    response_text: str = Field(min_length=1, description="Текст ответа ассистента")
    request_type: str = Field(min_length=1, max_length=32, description="Тип запроса")
