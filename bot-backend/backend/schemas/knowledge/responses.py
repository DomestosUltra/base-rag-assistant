from pydantic import BaseModel, Field


class KnowledgeSaveResponse(BaseModel):
    """Ответ сохранения базы знаний в векторную БД."""

    saved_chunks: int = Field(ge=0, description="Количество сохраненных чанков")


class KnowledgeDeleteResponse(BaseModel):
    """Ответ удаления данных из векторной БД."""

    deleted_count: int = Field(ge=0, description="Количество удаленных объектов")
