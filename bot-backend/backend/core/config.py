from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.core.enums import Environment


class AppSettings(BaseSettings):
    """Настройки приложения."""

    environment: Environment = Field(default=Environment.LOCAL, validation_alias="environment")
    log_level: str = Field(default="INFO", validation_alias="log_level")
    backend_api_key: str = Field(default="change-me", validation_alias="backend_api_key")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


class DatabaseSettings(BaseSettings):
    """Настройки базы данных."""

    host: str = Field(default="localhost", validation_alias="postgres_host")
    port: int = Field(default=5432, validation_alias="postgres_port")
    user: str = Field(default="rag_user", validation_alias="postgres_user")
    password: str = Field(default="rag_password", validation_alias="postgres_password")
    db: str = Field(default="rag_db", validation_alias="postgres_db")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @property
    def url(self) -> str:
        """Вернуть URL для асинхронного подключения к PostgreSQL.

        Returns:
            str: Строка подключения SQLAlchemy async.
        """
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
        )


class OpenAISettings(BaseSettings):
    """Настройки OpenAI."""

    api_key: str = Field(default="", validation_alias="openai_api_key")
    base_url: str = Field(
        default="https://api.openai.com/v1",
        validation_alias="openai_base_url",
    )
    chat_model: str = Field(default="gpt-4.1-mini", validation_alias="chat_model")
    vision_model: str = Field(default="gpt-4.1-mini", validation_alias="vision_model")
    audio_model: str = Field(default="gpt-4o-mini-transcribe", validation_alias="audio_model")
    embedding_model: str = Field(
        default="text-embedding-3-small",
        validation_alias="embedding_model",
    )

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


class WeaviateSettings(BaseSettings):
    """Настройки Weaviate."""

    url: str = Field(default="http://localhost:8080", validation_alias="weaviate_url")
    index_name: str = Field(default="KnowledgeChunk", validation_alias="weaviate_index_name")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


class Settings(BaseModel):
    """Корневые настройки приложения."""

    app: AppSettings = AppSettings()
    database: DatabaseSettings = DatabaseSettings()
    openai: OpenAISettings = OpenAISettings()
    weaviate: WeaviateSettings = WeaviateSettings()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Получить кэшированный объект настроек.

    Returns:
        Settings: Настройки приложения.
    """
    return Settings()
