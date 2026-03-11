from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DialogueResponse(BaseModel):
    """DTO ответа записи диалога."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="Идентификатор записи")
    user_id: str = Field(description="Идентификатор пользователя")
    request_text: str = Field(description="Текст запроса пользователя")
    response_text: str = Field(description="Текст ответа ассистента")
    request_type: str = Field(description="Тип запроса")
    created_at: datetime = Field(description="Время создания записи")
