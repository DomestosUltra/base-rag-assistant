from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.protocols.unit_of_work import UnitOfWork


class UnitOfWorkImpl(UnitOfWork):
    """Реализация Unit of Work на SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        """Зафиксировать транзакцию."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Откатить транзакцию."""
        await self._session.rollback()
