from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Настройки приложения."""

    log_level: str = Field(default="INFO", validation_alias="log_level")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


class BotSettings(BaseSettings):
    """Настройки Telegram бота."""

    token: str = Field(default="", validation_alias="bot_token")
    webhook_url: str = Field(
        default="http://localhost:8081/webhook/telegram",
        validation_alias="telegram_webhook_url",
    )
    webhook_path: str = Field(
        default="/webhook/telegram",
        validation_alias="telegram_webhook_path",
    )
    webhook_secret: str = Field(
        default="change-me",
        validation_alias="telegram_webhook_secret",
    )

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


class BackendSettings(BaseSettings):
    """Настройки backend API."""

    api_key: str = Field(default="change-me", validation_alias="backend_api_key")
    base_url: str = Field(default="http://backend:8000", validation_alias="backend_base_url")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


class Settings(BaseModel):
    """Корневой класс настроек бота."""

    app: AppSettings = AppSettings()
    bot: BotSettings = BotSettings()
    backend: BackendSettings = BackendSettings()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Получить настройки бота.

    Returns:
        Settings: Конфигурация сервиса.
    """
    return Settings()
