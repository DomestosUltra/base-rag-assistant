from starlette import status
from fastapi import APIRouter, Depends, Query
from dishka.integrations.fastapi import inject

from backend.api.v1.depends import KnowledgeStoreDep, UserIdDep, require_api_key
from backend.schemas.knowledge.requests import (
    KnowledgeSaveFileRequest,
    KnowledgeSaveTextRequest,
    KnowledgeSaveTextsRequest,
)
from backend.schemas.knowledge.responses import KnowledgeDeleteResponse, KnowledgeSaveResponse

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post(
    "/text",
    response_model=KnowledgeSaveResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def save_knowledge_text(
    request: KnowledgeSaveTextRequest,
    user_id: UserIdDep,
    knowledge_store: KnowledgeStoreDep,
) -> KnowledgeSaveResponse:
    """Сохранить один текст в векторную базу знаний.

    Args:
        request: DTO текстового документа.
        user_id: Идентификатор пользователя из заголовка.
        knowledge_store: Сервис хранилища знаний.

    Returns:
        KnowledgeSaveResponse: Количество сохраненных чанков.
    """
    saved_chunks = knowledge_store.save_document(document=request, ingested_by=user_id)
    return KnowledgeSaveResponse(saved_chunks=saved_chunks)


@router.post(
    "/texts",
    response_model=KnowledgeSaveResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def save_knowledge_texts(
    request: KnowledgeSaveTextsRequest,
    user_id: UserIdDep,
    knowledge_store: KnowledgeStoreDep,
) -> KnowledgeSaveResponse:
    """Сохранить пакет текстов в векторную базу знаний.

    Args:
        request: DTO списка текстов.
        user_id: Идентификатор пользователя из заголовка.
        knowledge_store: Сервис хранилища знаний.

    Returns:
        KnowledgeSaveResponse: Количество сохраненных чанков.
    """
    saved_chunks = knowledge_store.save_documents(
        documents=request.documents,
        ingested_by=user_id,
    )
    return KnowledgeSaveResponse(saved_chunks=saved_chunks)


@router.put(
    "/texts",
    response_model=KnowledgeSaveResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def upsert_knowledge_texts(
    request: KnowledgeSaveTextsRequest,
    user_id: UserIdDep,
    knowledge_store: KnowledgeStoreDep,
) -> KnowledgeSaveResponse:
    """Идемпотентно обновить/добавить пакет текстов в базу знаний.

    Args:
        request: DTO списка текстов.
        user_id: Идентификатор пользователя из заголовка.
        knowledge_store: Сервис хранилища знаний.

    Returns:
        KnowledgeSaveResponse: Количество сохраненных чанков.
    """
    saved_chunks = knowledge_store.save_documents(
        documents=request.documents,
        ingested_by=user_id,
    )
    return KnowledgeSaveResponse(saved_chunks=saved_chunks)


@router.post(
    "/file",
    response_model=KnowledgeSaveResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def save_knowledge_file(
    request: KnowledgeSaveFileRequest,
    user_id: UserIdDep,
    knowledge_store: KnowledgeStoreDep,
) -> KnowledgeSaveResponse:
    """Сохранить текст из файла в векторную базу знаний.

    Args:
        request: DTO пути к текстовому файлу.
        user_id: Идентификатор пользователя из заголовка.
        knowledge_store: Сервис хранилища знаний.

    Returns:
        KnowledgeSaveResponse: Количество сохраненных чанков.
    """
    saved_chunks = knowledge_store.save_from_file(request=request, ingested_by=user_id)
    return KnowledgeSaveResponse(saved_chunks=saved_chunks)


@router.put(
    "/file",
    response_model=KnowledgeSaveResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def upsert_knowledge_file(
    request: KnowledgeSaveFileRequest,
    user_id: UserIdDep,
    knowledge_store: KnowledgeStoreDep,
) -> KnowledgeSaveResponse:
    """Идемпотентно обновить/добавить текст из файла в базу знаний.

    Args:
        request: DTO пути к текстовому файлу.
        user_id: Идентификатор пользователя из заголовка.
        knowledge_store: Сервис хранилища знаний.

    Returns:
        KnowledgeSaveResponse: Количество сохраненных чанков.
    """
    saved_chunks = knowledge_store.save_from_file(request=request, ingested_by=user_id)
    return KnowledgeSaveResponse(saved_chunks=saved_chunks)


@router.delete(
    "/object/{object_id}",
    response_model=KnowledgeDeleteResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_api_key)],
)
@inject
async def delete_knowledge_object(
    object_id: str,
    knowledge_store: KnowledgeStoreDep,
) -> KnowledgeDeleteResponse:
    """Удалить объект базы знаний по UUID.

    Args:
        object_id: UUID объекта.
        knowledge_store: Сервис хранилища знаний.

    Returns:
        KnowledgeDeleteResponse: Количество удаленных объектов.
    """
    deleted_count = knowledge_store.delete_by_object_id(object_id)
    return KnowledgeDeleteResponse(deleted_count=deleted_count)


@router.delete(
    "/document/{document_id}",
    response_model=KnowledgeDeleteResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_api_key)],
)
@inject
async def delete_knowledge_document(
    document_id: str,
    knowledge_store: KnowledgeStoreDep,
) -> KnowledgeDeleteResponse:
    """Удалить документ базы знаний по document_id.

    Args:
        document_id: Внутренний document_id документа.
        knowledge_store: Сервис хранилища знаний.

    Returns:
        KnowledgeDeleteResponse: Количество удаленных объектов.
    """
    deleted_count = knowledge_store.delete_by_document_id(document_id)
    return KnowledgeDeleteResponse(deleted_count=deleted_count)


@router.delete(
    "/external/{external_id}",
    response_model=KnowledgeDeleteResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_api_key)],
)
@inject
async def delete_knowledge_external(
    external_id: str,
    knowledge_store: KnowledgeStoreDep,
) -> KnowledgeDeleteResponse:
    """Удалить документ базы знаний по external_id.

    Args:
        external_id: Внешний идентификатор документа.
        knowledge_store: Сервис хранилища знаний.

    Returns:
        KnowledgeDeleteResponse: Количество удаленных объектов.
    """
    deleted_count = knowledge_store.delete_by_external_id(external_id)
    return KnowledgeDeleteResponse(deleted_count=deleted_count)


@router.delete(
    "/all",
    response_model=KnowledgeDeleteResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_api_key)],
)
@inject
async def delete_knowledge_all(
    knowledge_store: KnowledgeStoreDep,
    confirm: bool = Query(default=False),
) -> KnowledgeDeleteResponse:
    """Удалить все данные базы знаний из векторной БД.

    Args:
        confirm: Подтверждение массового удаления.
        knowledge_store: Сервис хранилища знаний.

    Returns:
        KnowledgeDeleteResponse: Количество удаленных объектов.
    """
    if not confirm:
        return KnowledgeDeleteResponse(deleted_count=0)
    deleted_count = knowledge_store.delete_all()
    return KnowledgeDeleteResponse(deleted_count=deleted_count)
