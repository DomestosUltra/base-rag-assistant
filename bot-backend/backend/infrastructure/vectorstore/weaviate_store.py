from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import weaviate
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_weaviate import WeaviateVectorStore
from weaviate.classes.query import Filter
from uuid_utils import uuid7

from backend.core.config import OpenAISettings, WeaviateSettings
from backend.schemas.knowledge.requests import (
    KnowledgeDocumentRequest,
    KnowledgeMetadataRequest,
    KnowledgeSaveFileRequest,
)


class WeaviateKnowledgeStore:
    """Обертка для векторного хранилища Weaviate."""

    def __init__(self, settings: WeaviateSettings, openai: OpenAISettings) -> None:
        parsed = urlparse(settings.url)
        http_host = parsed.hostname or "localhost"
        http_port = parsed.port or 8080
        http_secure = parsed.scheme == "https"
        self._client = weaviate.connect_to_custom(
            http_host=http_host,
            http_port=http_port,
            http_secure=http_secure,
            grpc_host=http_host,
            grpc_port=50051,
            grpc_secure=False,
        )
        self._embeddings = OpenAIEmbeddings(
            model=openai.embedding_model,
            api_key=openai.api_key,
            base_url=openai.base_url,
        )
        self._vector_store = WeaviateVectorStore(
            client=self._client,
            index_name=settings.index_name,
            text_key="text",
            embedding=self._embeddings,
        )
        self._index_name = settings.index_name
        self._splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)

    async def search(
        self,
        query: str,
        user_id: str,
        search_shared: bool,
        k: int = 4,
    ) -> list[str]:
        """Выполнить семантический поиск по базе знаний.

        Args:
            query: Поисковый запрос.
            user_id: Идентификатор пользователя.
            search_shared: Флаг поиска по общей базе знаний.
            k: Количество документов.

        Returns:
            list[str]: Тексты найденных документов.
        """
        docs = await self._vector_store.asimilarity_search(query, k=max(k * 8, 20))
        visible_docs: list[str] = []
        for document in docs:
            metadata = document.metadata or {}
            scope = str(metadata.get("collection_scope") or "shared")
            ingested_by = str(metadata.get("ingested_by") or "")
            if scope == "personal" and ingested_by != user_id:
                continue
            if scope == "shared" and not search_shared:
                continue
            visible_docs.append(document.page_content)
            if len(visible_docs) >= k:
                break
        return visible_docs

    def _build_chunk_metadata(
        self,
        metadata: KnowledgeMetadataRequest,
        document_id: str,
        chunk_index: int,
        chunks_total: int,
        ingested_by: str,
    ) -> dict[str, Any]:
        """Построить metadata для чанка документа.

        Args:
            metadata: Базовые metadata документа.
            document_id: Уникальный идентификатор документа.
            chunk_index: Порядковый номер чанка.
            chunks_total: Общее количество чанков.
            ingested_by: Идентификатор пользователя, выполнившего загрузку.

        Returns:
            dict[str, Any]: Словарь metadata для сохранения в Weaviate.
        """
        return {
            "document_id": document_id,
            "chunk_index": chunk_index,
            "chunks_total": chunks_total,
            "collection_scope": metadata.collection_scope,
            "title": metadata.title,
            "source": metadata.source,
            "source_type": metadata.source_type,
            "category": metadata.category,
            "language": metadata.language,
            "author": metadata.author,
            "external_id": metadata.external_id,
            "tags": metadata.tags,
            "created_at": metadata.created_at.isoformat() if metadata.created_at else None,
            "ingested_at": datetime.now(UTC).isoformat(),
            "ingested_by": ingested_by,
        }

    def _prepare_document_chunks(
        self,
        document: KnowledgeDocumentRequest,
        ingested_by: str,
    ) -> tuple[list[str], list[dict[str, Any]]]:
        """Подготовить чанки и metadata документа к записи.

        Args:
            document: DTO документа базы знаний.
            ingested_by: Идентификатор пользователя, выполнившего загрузку.

        Returns:
            tuple[list[str], list[dict[str, Any]]]: Чанки текста и metadata чанков.
        """
        normalized_text = document.text.strip()
        if not normalized_text:
            return [], []

        chunks = self._splitter.split_text(normalized_text)
        if not chunks:
            return [], []

        document_id = str(uuid7())
        chunks_total = len(chunks)
        metadatas = [
            self._build_chunk_metadata(
                metadata=document.metadata,
                document_id=document_id,
                chunk_index=chunk_index,
                chunks_total=chunks_total,
                ingested_by=ingested_by,
            )
            for chunk_index in range(chunks_total)
        ]
        return chunks, metadatas

    def save_documents(self, documents: list[KnowledgeDocumentRequest], ingested_by: str) -> int:
        """Сохранить набор документов базы знаний в векторную БД.

        Args:
            documents: Список документов базы знаний.
            ingested_by: Идентификатор пользователя, выполнившего загрузку.

        Returns:
            int: Количество сохраненных чанков.
        """
        prepared_chunks: list[str] = []
        prepared_metadatas: list[dict[str, Any]] = []
        for document in documents:
            chunks, metadatas = self._prepare_document_chunks(document=document, ingested_by=ingested_by)
            prepared_chunks.extend(chunks)
            prepared_metadatas.extend(metadatas)
        if not prepared_chunks:
            return 0
        self._vector_store.add_texts(texts=prepared_chunks, metadatas=prepared_metadatas)
        return len(prepared_chunks)

    def save_document(self, document: KnowledgeDocumentRequest, ingested_by: str) -> int:
        """Сохранить один текстовый документ в векторную БД.

        Args:
            document: DTO документа базы знаний.
            ingested_by: Идентификатор пользователя, выполнившего загрузку.

        Returns:
            int: Количество сохраненных чанков.
        """
        return self.save_documents(documents=[document], ingested_by=ingested_by)

    def save_from_file(self, request: KnowledgeSaveFileRequest, ingested_by: str) -> int:
        """Сохранить содержимое файла базы знаний в векторную БД.

        Args:
            request: DTO запроса загрузки из файла.
            ingested_by: Идентификатор пользователя, выполнившего загрузку.

        Raises:
            FileNotFoundError: Если файл не найден.

        Returns:
            int: Количество сохраненных чанков.
        """
        path = Path(request.file_path)
        if not path.exists():
            raise FileNotFoundError(request.file_path)
        text = path.read_text(encoding="utf-8")
        return self.save_document(
            document=KnowledgeDocumentRequest(text=text, metadata=request.metadata),
            ingested_by=ingested_by,
        )

    def _fetch_ids_by_filter(self, filters: Filter) -> list[str]:
        """Получить идентификаторы объектов по фильтру.

        Args:
            filters: Фильтр выборки объектов.

        Returns:
            list[str]: Список UUID объектов.
        """
        collection = self._client.collections.get(self._index_name)
        offset = 0
        limit = 100
        object_ids: list[str] = []
        while True:
            response = collection.query.fetch_objects(
                filters=filters,
                limit=limit,
                offset=offset,
            )
            objects = response.objects
            if not objects:
                break
            object_ids.extend(str(obj.uuid) for obj in objects)
            if len(objects) < limit:
                break
            offset += limit
        return object_ids

    def _delete_ids(self, object_ids: list[str]) -> int:
        """Удалить объекты по UUID.

        Args:
            object_ids: Список UUID для удаления.

        Returns:
            int: Количество удаленных объектов.
        """
        if not object_ids:
            return 0
        self._vector_store.delete(ids=object_ids)
        return len(object_ids)

    def delete_by_object_id(self, object_id: str) -> int:
        """Удалить объект из векторной БД по UUID.

        Args:
            object_id: UUID объекта.

        Returns:
            int: Количество удаленных объектов.
        """
        return self._delete_ids([object_id])

    def delete_by_document_id(self, document_id: str) -> int:
        """Удалить все чанки документа по document_id.

        Args:
            document_id: Внутренний document_id документа.

        Returns:
            int: Количество удаленных объектов.
        """
        ids = self._fetch_ids_by_filter(
            Filter.by_property("document_id").equal(document_id)
        )
        return self._delete_ids(ids)

    def delete_by_external_id(self, external_id: str) -> int:
        """Удалить все чанки документа по external_id.

        Args:
            external_id: Внешний идентификатор документа.

        Returns:
            int: Количество удаленных объектов.
        """
        ids = self._fetch_ids_by_filter(
            Filter.by_property("external_id").equal(external_id)
        )
        return self._delete_ids(ids)

    def delete_all(self) -> int:
        """Удалить все объекты класса базы знаний.

        Returns:
            int: Количество удаленных объектов.
        """
        collection = self._client.collections.get(self._index_name)
        offset = 0
        limit = 100
        object_ids: list[str] = []
        while True:
            response = collection.query.fetch_objects(limit=limit, offset=offset)
            objects = response.objects
            if not objects:
                break
            object_ids.extend(str(obj.uuid) for obj in objects)
            if len(objects) < limit:
                break
            offset += limit
        return self._delete_ids(object_ids)
