from enum import StrEnum


class Environment(StrEnum):
    """Перечисление окружений приложения."""

    LOCAL = "local"
    DEV = "dev"
    STAGE = "stage"
    PROD = "prod"
