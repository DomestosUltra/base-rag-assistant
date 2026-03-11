from backend.domain.models.dialogue import DialogueRecord
from backend.domain.repositories.dialogue_repository import DialogueRepository
from backend.domain.services.dialogue_service import DialogueService
from backend.schemas.dialogue.requests import DialogueCreateRequest


class DialogueServiceImpl(DialogueService):
    """Сервис для сохранения истории диалога."""

    def __init__(self, repository: DialogueRepository) -> None:
        self._repository = repository

    async def log_dialogue(
        self,
        request: DialogueCreateRequest,
    ) -> DialogueRecord:
        """Сохранить диалог пользователя.

        Args:
            request: DTO запроса на запись диалога.

        Returns:
            DialogueRecord: Сохраненная запись.
        """
        return await self._repository.create(request)

    async def get_recent_messages(self, user_id: str, limit: int = 10) -> list[str]:
        """Получить последние сообщения диалога пользователя.

        Args:
            user_id: Идентификатор пользователя.
            limit: Количество последних сообщений.

        Returns:
            list[str]: Последние сообщения в формате истории.
        """
        records = await self._repository.get_recent_by_user(user_id=user_id, limit=limit)
        history: list[str] = []
        for record in reversed(records):
            history.append(f"Пользователь: {record.request_text}")
            history.append(f"Ассистент: {record.response_text}")
        return history[-limit:]

    async def clear_history(self, user_id: str) -> bool:
        """Очистить историю диалога пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            bool: Признак успешной очистки.
        """
        deleted_count = await self._repository.delete_by_user(user_id=user_id)
        return deleted_count > 0
