from collections.abc import AsyncIterable

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import FastapiProvider
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import DatabaseSettings, OpenAISettings, Settings, WeaviateSettings, get_settings
from backend.domain.repositories.dialogue_repository import DialogueRepository
from backend.domain.services.dialogue_service import DialogueService
from backend.domain.services.rag_service import RagService
from backend.infrastructure.db.session import DatabaseManager
from backend.infrastructure.db.unit_of_work import UnitOfWorkImpl
from backend.infrastructure.repositories.dialogue_repository import DialogueRepositoryImpl
from backend.infrastructure.services.dialogue_service import DialogueServiceImpl
from backend.infrastructure.services.media_service import MediaService
from backend.infrastructure.services.rag_service import RagServiceImpl
from backend.infrastructure.vectorstore.weaviate_store import WeaviateKnowledgeStore


class BackendProvider(Provider):
    """Dishka provider backend сервиса."""

    @provide(scope=Scope.APP)
    def get_app_settings(self) -> Settings:
        """Получить настройки приложения."""
        return get_settings()

    @provide(scope=Scope.APP)
    def get_openai_settings(self, settings: Settings) -> OpenAISettings:
        """Получить настройки OpenAI."""
        return settings.openai

    @provide(scope=Scope.APP)
    def get_weaviate_settings(self, settings: Settings) -> WeaviateSettings:
        """Получить настройки Weaviate."""
        return settings.weaviate

    @provide(scope=Scope.APP)
    def get_database_settings(self, settings: Settings) -> DatabaseSettings:
        """Получить настройки базы данных."""
        return settings.database

    @provide(scope=Scope.APP)
    async def get_db_manager(self, settings: Settings) -> AsyncIterable[DatabaseManager]:
        """Создать менеджер БД уровня приложения."""
        manager = DatabaseManager(database_url=settings.database.url)
        yield manager
        await manager.close()

    @provide(scope=Scope.REQUEST)
    async def get_db_session(self, db_manager: DatabaseManager) -> AsyncIterable[AsyncSession]:
        """Создать сессию БД на время запроса."""
        async for session in db_manager.get_session():
            yield session

    @provide(scope=Scope.APP)
    def get_knowledge_store(self, settings: Settings) -> WeaviateKnowledgeStore:
        """Создать Weaviate knowledge store."""
        return WeaviateKnowledgeStore(settings=settings.weaviate, openai=settings.openai)

    @provide(scope=Scope.APP)
    def get_media_service(self, settings: Settings) -> MediaService:
        """Создать сервис обработки медиа."""
        return MediaService(settings=settings.openai)

    dialogue_repository = provide(
        DialogueRepositoryImpl,
        provides=DialogueRepository,
        scope=Scope.REQUEST,
    )
    dialogue_service = provide(
        DialogueServiceImpl,
        provides=DialogueService,
        scope=Scope.REQUEST,
    )
    rag_service = provide(
        RagServiceImpl,
        provides=RagService,
        scope=Scope.APP,
    )
    unit_of_work = provide(UnitOfWorkImpl, scope=Scope.REQUEST)


def create_container() -> AsyncContainer:
    """Создать корневой dishka контейнер backend."""
    return make_async_container(BackendProvider(), FastapiProvider())
