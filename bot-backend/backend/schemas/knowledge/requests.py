from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class KnowledgeMetadataRequest(BaseModel):
    """Метаданные документа базы знаний."""

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
    tags: list[str] = Field(default_factory=list, description="Список тегов документа")
    created_at: datetime | None = Field(
        default=None, description="Время создания исходного документа"
    )


class KnowledgeDocumentRequest(BaseModel):
    """Документ для сохранения в базу знаний."""

    text: str = Field(min_length=1, description="Текст документа базы знаний")
    metadata: KnowledgeMetadataRequest = Field(
        default_factory=KnowledgeMetadataRequest,
        description="Метаданные документа",
    )


class KnowledgeSaveTextRequest(KnowledgeDocumentRequest):
    """Запрос на сохранение одного текста в базу знаний."""


class KnowledgeSaveTextsRequest(BaseModel):
    """Запрос на пакетное сохранение текстов в базу знаний."""

    documents: list[KnowledgeDocumentRequest] = Field(
        min_length=1,
        description="Список документов базы знаний",
    )


class KnowledgeSaveFileRequest(BaseModel):
    """Запрос на сохранение текста из файла в базу знаний."""

    file_path: str = Field(min_length=1, description="Путь к файлу (.txt или .docx)")
    metadata: KnowledgeMetadataRequest = Field(
        default_factory=KnowledgeMetadataRequest,
        description="Метаданные документа",
    )


class KnowledgeDeleteByObjectIdRequest(BaseModel):
    """Запрос на удаление объекта по UUID в векторной БД."""

    object_id: str = Field(min_length=1, description="UUID объекта в Weaviate")


class KnowledgeDeleteByDocumentIdRequest(BaseModel):
    """Запрос на удаление документа по document_id из векторной БД."""

    document_id: str = Field(min_length=1, description="Внутренний document_id документа")


class KnowledgeDeleteByExternalIdRequest(BaseModel):
    """Запрос на удаление документа по external_id из векторной БД."""

    external_id: str = Field(min_length=1, description="Внешний идентификатор документа")


class KnowledgeDeleteAllRequest(BaseModel):
    """Запрос на удаление всех объектов класса векторной БД."""

    confirm: bool = Field(description="Подтверждение массового удаления")
