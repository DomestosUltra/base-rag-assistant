from abc import ABC, abstractmethod


class RagService(ABC):
    """Интерфейс RAG сервиса."""

    @abstractmethod
    async def ask(
        self,
        user_id: str,
        text: str,
        history_messages: list[str],
        image_context: str | None,
        request_type: str,
        search_shared: bool,
    ) -> str:
        """Сформировать ответ на запрос пользователя.

        Args:
            user_id: Идентификатор пользователя.
            text: Текст запроса.
            history_messages: Последние сообщения истории диалога.
            image_context: Распознанный контекст картинки.
            request_type: Тип запроса.
            search_shared: Флаг поиска по общей базе знаний.

        Returns:
            str: Ответ модели.
        """
