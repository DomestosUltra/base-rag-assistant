from typing import Literal

from pydantic import BaseModel, Field


class TelegramMessageDTO(BaseModel):
    """DTO сообщения Telegram для backend API."""

    user_id: str = Field(description="Идентификатор пользователя")
    text: str = Field(description="Текст запроса")


class TelegramKnowledgeMetadataDTO(BaseModel):
    """DTO metadata для сохранения знаний из Telegram."""

    title: str | None = Field(default=None, description="Заголовок документа")
    source: str | None = Field(default=None, description="Источник документа")
    source_type: str | None = Field(default=None, description="Тип источника")
    category: str | None = Field(default=None, description="Категория документа")
    language: str | None = Field(default=None, description="Язык документа")
    author: str | None = Field(default=None, description="Автор документа")
    external_id: str | None = Field(default=None, description="Внешний идентификатор документа")
    collection_scope: Literal["shared", "personal"] = Field(
        default="shared",
        description="Область видимости документа: shared или personal",
    )
    tags: list[str] = Field(default_factory=list, description="Теги документа")


class TelegramKnowledgeSaveTextDTO(BaseModel):
    """DTO запроса на сохранение текста в базу знаний."""

    user_id: str = Field(description="Идентификатор пользователя")
    text: str = Field(min_length=1, description="Текст для сохранения")
    metadata: TelegramKnowledgeMetadataDTO = Field(
        default_factory=TelegramKnowledgeMetadataDTO,
        description="Метаданные документа",
    )


class TelegramVoiceDTO(BaseModel):
    """DTO запроса на обработку голосового сообщения."""

    user_id: str = Field(description="Идентификатор пользователя")
    audio_bytes: bytes = Field(description="Бинарное содержимое аудио")
    file_name: str = Field(description="Имя аудиофайла")
    content_type: str = Field(description="MIME тип аудиофайла")


class TelegramPhotoDTO(BaseModel):
    """DTO запроса на обработку изображения."""

    user_id: str = Field(description="Идентификатор пользователя")
    text: str = Field(description="Текстовый запрос для multimodal endpoint")
    image_bytes: bytes = Field(description="Бинарное содержимое изображения")
    file_name: str = Field(description="Имя файла изображения")
    content_type: str = Field(description="MIME тип изображения")


class TelegramUserSettingsDTO(BaseModel):
    """DTO пользовательских настроек Telegram бота."""

    save_scope: Literal["shared", "personal"] = Field(
        default="shared",
        description="Режим сохранения данных",
    )
    search_shared: bool = Field(
        default=True,
        description="Искать ли по общим данным",
    )
