from abc import ABC, abstractmethod

from backend.domain.models.dialogue import DialogueRecord
from backend.schemas.dialogue.requests import DialogueCreateRequest


class DialogueService(ABC):
    """Интерфейс сервиса записи диалогов."""

    @abstractmethod
    async def log_dialogue(
        self,
        request: DialogueCreateRequest,
    ) -> DialogueRecord:
        """Сохранить запрос и ответ пользователя.

        Args:
            request: DTO запроса на запись диалога.

        Returns:
            DialogueRecord: Сохраненная запись.
        """

    @abstractmethod
    async def get_recent_messages(self, user_id: str, limit: int = 10) -> list[str]:
        """Получить последние сообщения диалога пользователя.

        Args:
            user_id: Идентификатор пользователя.
            limit: Количество последних сообщений.

        Returns:
            list[str]: Последние сообщения в формате истории.
        """

    @abstractmethod
    async def clear_history(self, user_id: str) -> bool:
        """Очистить историю диалога пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            bool: Признак успешной очистки.
        """
