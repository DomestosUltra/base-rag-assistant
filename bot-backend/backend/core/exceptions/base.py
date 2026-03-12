from abc import ABC, abstractmethod


class CustomException(Exception, ABC):
    """Базовое бизнес-исключение приложения."""

    @property
    @abstractmethod
    def status_code(self) -> int:
        """Вернуть HTTP статус для исключения.

        Returns:
            int: HTTP статус-код.
        """

    @property
    @abstractmethod
    def errors(self) -> dict[str, str]:
        """Вернуть структуру ошибки.

        Returns:
            dict[str, str]: Ошибка на русском и английском.
        """


def generate_responses_from_exceptions(
    *exceptions: CustomException,
) -> dict[int, dict[str, object]]:
    """Сгенерировать OpenAPI responses из исключений.

    Args:
        exceptions: Экземпляры исключений.

    Returns:
        dict[int, dict[str, object]]: Карта ответов для OpenAPI.
    """
    responses: dict[int, dict[str, object]] = {}
    for exception in exceptions:
        code = exception.status_code
        payload: dict[str, object] = {
            "description": exception.errors.get("message", "Ошибка"),
            "content": {"application/json": {"example": exception.errors}},
        }
        responses[code] = payload
    return responses
