from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Header

from backend.core.config import Settings, get_settings
from backend.core.exceptions import AuthenticationError
from backend.domain.services.dialogue_service import DialogueService
from backend.domain.services.rag_service import RagService
from backend.infrastructure.db.unit_of_work import UnitOfWorkImpl
from backend.infrastructure.services.media_service import MediaService
from backend.infrastructure.vectorstore.weaviate_store import WeaviateKnowledgeStore


@inject
async def get_api_user(
    x_api_key: Annotated[str, Header(alias="X-API-Key")],
    x_user_id: Annotated[str, Header(alias="X-User-Id")],
    settings: FromDishka[Settings],
) -> str:
    """Проверить API ключ и вернуть user_id.

    Args:
        x_api_key: Ключ API из заголовка.
        x_user_id: Идентификатор пользователя.
        settings: Настройки приложения.

    Returns:
        str: Идентификатор пользователя.

    Raises:
        AuthenticationError: Если API ключ неверен.
    """
    if x_api_key != settings.app.backend_api_key:
        raise AuthenticationError()
    return x_user_id


@inject
async def validate_api_key(
    x_api_key: Annotated[str, Header(alias="X-API-Key")],
    settings: FromDishka[Settings],
) -> str:
    """Проверить API ключ.

    Args:
        x_api_key: Ключ API из заголовка.
        settings: Настройки приложения.

    Raises:
        AuthenticationError: Если API ключ неверен.

    Returns:
        str: Проверенный API ключ.
    """
    if x_api_key != settings.app.backend_api_key:
        raise AuthenticationError()
    return x_api_key


def require_api_key(
    x_api_key: Annotated[str, Header(alias="X-API-Key")],
    settings: Annotated[Settings, Depends(get_settings)],
) -> str:
    """Проверить API ключ через стандартную fastapi dependency.

    Args:
        x_api_key: Ключ API из заголовка.
        settings: Настройки приложения.

    Raises:
        AuthenticationError: Если API ключ неверен.

    Returns:
        str: Проверенный API ключ.
    """
    if x_api_key != settings.app.backend_api_key:
        raise AuthenticationError()
    return x_api_key


UserIdDep = Annotated[str, Depends(get_api_user)]
ApiKeyDep = Annotated[str, Depends(validate_api_key)]
DialogueServiceDep = FromDishka[DialogueService]
RagServiceDep = FromDishka[RagService]
UnitOfWorkDep = FromDishka[UnitOfWorkImpl]
MediaServiceDep = FromDishka[MediaService]
KnowledgeStoreDep = FromDishka[WeaviateKnowledgeStore]
