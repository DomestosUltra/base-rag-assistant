from abc import ABC, abstractmethod

from backend.domain.models.dialogue import DialogueRecord
from backend.schemas.dialogue.requests import DialogueCreateRequest


class DialogueRepository(ABC):
    """Интерфейс репозитория записей диалогов."""

    @abstractmethod
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

    @abstractmethod
    async def get_recent_by_user(self, user_id: str, limit: int) -> list[DialogueRecord]:
        """Получить последние записи диалога пользователя.

        Args:
            user_id: Идентификатор пользователя.
            limit: Количество последних записей.

        Returns:
            list[DialogueRecord]: Список записей диалога.
        """

    @abstractmethod
    async def delete_by_user(self, user_id: str) -> int:
        """Удалить все записи диалога пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            int: Количество удаленных записей.
        """
