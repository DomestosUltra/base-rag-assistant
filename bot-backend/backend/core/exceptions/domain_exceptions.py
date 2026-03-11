from backend.core.exceptions.base import CustomException


class AuthenticationError(CustomException):
    """Ошибка аутентификации API ключа."""

    @property
    def status_code(self) -> int:
        """Вернуть статус ошибки аутентификации.

        Returns:
            int: HTTP статус код.
        """
        return 401

    @property
    def errors(self) -> dict[str, str]:
        """Вернуть тело ошибки аутентификации.

        Returns:
            dict[str, str]: Структурированная ошибка.
        """
        return {
            "message": "Неверный API ключ",
            "messageEn": "Invalid API key",
        }


class DialogueNotFoundError(CustomException):
    """Ошибка отсутствия диалога пользователя."""

    def __init__(self, user_id: str) -> None:
        self._user_id = user_id

    @property
    def status_code(self) -> int:
        """Вернуть статус ошибки отсутствия диалога.

        Returns:
            int: HTTP статус код.
        """
        return 404

    @property
    def errors(self) -> dict[str, str]:
        """Вернуть тело ошибки отсутствия диалога.

        Returns:
            dict[str, str]: Структурированная ошибка.
        """
        return {
            "message": f"Диалог для пользователя {self._user_id} не найден",
            "messageEn": f"Dialogue for user {self._user_id} was not found",
        }
