from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel
from uuid_utils import uuid7


class DialogueRecord(SQLModel, table=True):
    """Модель записи диалога пользователя."""

    __tablename__ = "dialogue_records"

    id: UUID = Field(default_factory=uuid7, primary_key=True, description="ID записи")
    user_id: str = Field(index=True, max_length=128, description="Идентификатор пользователя")
    request_text: str = Field(description="Текст запроса пользователя")
    response_text: str = Field(description="Ответ ассистента")
    request_type: str = Field(max_length=32, description="Тип запроса")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="Время",
    )
