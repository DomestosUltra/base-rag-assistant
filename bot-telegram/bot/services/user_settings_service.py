from typing import Literal

from bot.dto.message import TelegramUserSettingsDTO


class UserSettingsService:
    """Сервис хранения пользовательских настроек Telegram бота."""

    def __init__(self) -> None:
        self._settings_by_user: dict[str, TelegramUserSettingsDTO] = {}

    def get(self, user_id: str) -> TelegramUserSettingsDTO:
        """Получить настройки пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            TelegramUserSettingsDTO: Текущие настройки пользователя.
        """
        settings = self._settings_by_user.get(user_id)
        if settings is None:
            settings = TelegramUserSettingsDTO()
            self._settings_by_user[user_id] = settings
        return settings

    def set_save_scope(self, user_id: str, scope: Literal["shared", "personal"]) -> TelegramUserSettingsDTO:
        """Установить режим сохранения пользователя.

        Args:
            user_id: Идентификатор пользователя.
            scope: Режим сохранения shared или personal.

        Returns:
            TelegramUserSettingsDTO: Обновленные настройки.
        """
        settings = self.get(user_id)
        updated = settings.model_copy(update={"save_scope": scope})
        self._settings_by_user[user_id] = updated
        return updated

    def toggle_search_shared(self, user_id: str) -> TelegramUserSettingsDTO:
        """Переключить режим поиска по общим данным.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            TelegramUserSettingsDTO: Обновленные настройки.
        """
        settings = self.get(user_id)
        updated = settings.model_copy(update={"search_shared": not settings.search_shared})
        self._settings_by_user[user_id] = updated
        return updated
