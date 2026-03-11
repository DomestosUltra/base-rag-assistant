from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


class DatabaseManager:
    """Менеджер подключений к базе данных."""

    def __init__(self, database_url: str) -> None:
        self._engine: AsyncEngine = create_async_engine(database_url, pool_pre_ping=True)
        self._session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Вернуть фабрику сессий.

        Returns:
            async_sessionmaker[AsyncSession]: Фабрика сессий.
        """
        return self._session_factory

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Создать сессию БД.

        Yields:
            AsyncSession: Асинхронная сессия.
        """
        async with self._session_factory() as session:
            yield session

    async def close(self) -> None:
        """Закрыть соединения с БД."""
        await self._engine.dispose()
