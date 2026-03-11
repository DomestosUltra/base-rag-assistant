from typing import Annotated

from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, File, Form, UploadFile
from starlette import status

from backend.api.v1.depends import (
    DialogueServiceDep,
    MediaServiceDep,
    RagServiceDep,
    UnitOfWorkDep,
    UserIdDep,
)
from backend.schemas.dialogue.requests import DialogueCreateRequest
from backend.schemas.query.requests import ClearMemoryRequest, TextImageRequest
from backend.schemas.query.responses import ClearMemoryResponse, QueryResponse

router = APIRouter(prefix="/query", tags=["query"])


@router.post(
    "/text-image",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def ask_text_or_text_image(
    request: Annotated[TextImageRequest, Depends(TextImageRequest.as_form)],
    user_id: UserIdDep,
    rag_service: RagServiceDep,
    dialogue_service: DialogueServiceDep,
    uow: UnitOfWorkDep,
    media_service: MediaServiceDep,
    image: UploadFile | None = File(default=None),
) -> QueryResponse:
    """Обработать текстовый запрос с опциональным изображением.

    Args:
        request: DTO текстового запроса.
        user_id: Идентификатор пользователя из заголовка.
        rag_service: Сервис RAG.
        dialogue_service: Сервис записи диалога.
        uow: Unit of Work.
        image: Опциональное изображение.

    Returns:
        QueryResponse: Ответ ассистента.
    """
    image_context = None
    if image is not None:
        image_bytes = await image.read()
        image_context = await media_service.describe_image(image_bytes)

    history_messages = await dialogue_service.get_recent_messages(user_id=user_id, limit=10)
    answer = await rag_service.ask(
        user_id=user_id,
        text=request.text,
        history_messages=history_messages,
        image_context=image_context,
        request_type="text-image",
        search_shared=request.search_shared,
    )
    await dialogue_service.log_dialogue(
        DialogueCreateRequest(
            user_id=user_id,
            request_text=request.text,
            response_text=answer,
            request_type="text-image",
        )
    )
    await uow.commit()
    return QueryResponse(answer=answer)


@router.post(
    "/audio-image",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def ask_audio_or_audio_image(
    user_id: UserIdDep,
    rag_service: RagServiceDep,
    dialogue_service: DialogueServiceDep,
    uow: UnitOfWorkDep,
    media_service: MediaServiceDep,
    audio: UploadFile = File(),
    image: UploadFile | None = File(default=None),
    search_shared: bool = Form(default=True),
) -> QueryResponse:
    """Обработать аудиозапрос с опциональным изображением.

    Args:
        user_id: Идентификатор пользователя из заголовка.
        rag_service: Сервис RAG.
        dialogue_service: Сервис записи диалога.
        uow: Unit of Work.
        audio: MP3 файл.
        image: Опциональное изображение.

    Returns:
        QueryResponse: Ответ ассистента.
    """
    audio_bytes = await audio.read()
    audio_text = await media_service.transcribe_audio(
        content=audio_bytes,
        file_name=audio.filename or "voice.ogg",
        content_type=audio.content_type or "application/octet-stream",
    )
    image_context = None
    if image is not None:
        image_bytes = await image.read()
        image_context = await media_service.describe_image(image_bytes)

    history_messages = await dialogue_service.get_recent_messages(user_id=user_id, limit=10)
    answer = await rag_service.ask(
        user_id=user_id,
        text=audio_text,
        history_messages=history_messages,
        image_context=image_context,
        request_type="audio-image",
        search_shared=search_shared,
    )
    await dialogue_service.log_dialogue(
        DialogueCreateRequest(
            user_id=user_id,
            request_text=audio_text,
            response_text=answer,
            request_type="audio-image",
        )
    )
    await uow.commit()
    return QueryResponse(answer=answer)


@router.post(
    "/memory/clear",
    response_model=ClearMemoryResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def clear_memory(
    request: ClearMemoryRequest,
    user_id: UserIdDep,
    dialogue_service: DialogueServiceDep,
    uow: UnitOfWorkDep,
) -> ClearMemoryResponse:
    """Очистить память диалога пользователя.

    Args:
        request: DTO запроса очистки.
        user_id: Идентификатор пользователя из заголовка.
        rag_service: Сервис RAG.

    Returns:
        ClearMemoryResponse: Результат очистки.
    """
    target_user_id = request.user_id if request.user_id else user_id
    cleared = await dialogue_service.clear_history(target_user_id)
    await uow.commit()
    return ClearMemoryResponse(cleared=cleared)
