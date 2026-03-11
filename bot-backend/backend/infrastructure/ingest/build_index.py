from backend.core.config import get_settings
from backend.schemas.knowledge.requests import KnowledgeSaveFileRequest
from backend.infrastructure.vectorstore.weaviate_store import WeaviateKnowledgeStore


def build_index_from_file(file_path: str) -> int:
    """Построить векторный индекс из текстового файла.

    Args:
        file_path: Путь к исходному текстовому документу.

    Raises:
        FileNotFoundError: Если файл не найден.

    Returns:
        int: Количество сохраненных чанков.
    """
    settings = get_settings()
    store = WeaviateKnowledgeStore(settings=settings.weaviate, openai=settings.openai)
    request = KnowledgeSaveFileRequest(file_path=file_path)
    return store.save_from_file(request=request, ingested_by="system")
