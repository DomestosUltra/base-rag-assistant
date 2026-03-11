class ConversationMemoryStore:
    """Хранилище контекста диалога по пользователям."""

    def __init__(self, max_messages: int = 10) -> None:
        self._max_messages = max_messages
        self._memory: dict[str, list[str]] = {}

    def append(self, user_id: str, message: str) -> None:
        """Добавить сообщение в память пользователя.

        Args:
            user_id: Идентификатор пользователя.
            message: Текст сообщения.
        """
        messages = self._memory.get(user_id, [])
        messages.append(message)
        self._memory[user_id] = messages[-self._max_messages :]

    def get_messages(self, user_id: str) -> list[str]:
        """Получить сообщения из памяти пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            list[str]: История сообщений.
        """
        return self._memory.get(user_id, [])

    def clear(self, user_id: str) -> bool:
        """Очистить память пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            bool: Удалены ли данные.
        """
        existed = user_id in self._memory
        if existed:
            del self._memory[user_id]
        return existed
