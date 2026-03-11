from typing import Protocol, runtime_checkable


@runtime_checkable
class UnitOfWork(Protocol):
    """Протокол Unit of Work для транзакций."""

    async def commit(self) -> None:
        """Зафиксировать изменения в транзакции."""

    async def rollback(self) -> None:
        """Откатить изменения в транзакции."""
