from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from backend.domain.models.dialogue import DialogueRecord
from backend.domain.repositories.dialogue_repository import DialogueRepository
from backend.schemas.dialogue.requests import DialogueCreateRequest


class DialogueRepositoryImpl(DialogueRepository):
    """SQL реализация репозитория диалогов."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        request: DialogueCreateRequest,
    ) -> DialogueRecord:
        """Создать запись диалога.

        Args:
            request: DTO запроса на создание записи диалога.

        Returns:
            DialogueRecord: Созданная запись.
        """
        record = DialogueRecord(
            user_id=request.user_id,
            request_text=request.request_text,
            response_text=request.response_text,
            request_type=request.request_type,
        )
        self._session.add(record)
        await self._session.flush()
        return record

    async def get_recent_by_user(self, user_id: str, limit: int) -> list[DialogueRecord]:
        """Получить последние записи диалога пользователя.

        Args:
            user_id: Идентификатор пользователя.
            limit: Количество записей.

        Returns:
            list[DialogueRecord]: Список записей.
        """
        statement = select(DialogueRecord).where(col(DialogueRecord.user_id) == user_id)
        statement = statement.order_by(col(DialogueRecord.created_at).desc()).limit(limit)
        result = await self._session.execute(statement)
        return list(result.scalars().all())

    async def delete_by_user(self, user_id: str) -> int:
        """Удалить все записи диалога пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            int: Количество удаленных записей.
        """
        count_statement = (
            select(func.count())
            .select_from(DialogueRecord)
            .where(col(DialogueRecord.user_id) == user_id)
        )
        count_result = await self._session.execute(count_statement)
        deleted_count = int(count_result.scalar_one())
        if deleted_count == 0:
            return 0
        statement = delete(DialogueRecord).where(col(DialogueRecord.user_id) == user_id)
        await self._session.execute(statement)
        return deleted_count
