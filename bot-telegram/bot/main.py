from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramAPIError
from aiogram.types import BotCommand
from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request
from starlette import status

from bot.core.config import Settings, get_settings
from bot.core.logging import configure_logging
from bot.factories.service_factory import TelegramServiceFactory
from bot.handlers.media_handler import MediaHandler
from bot.handlers.message_handler import MessageHandler
from bot.services.user_settings_service import UserSettingsService

logger = logging.getLogger(__name__)


def build_dispatcher(settings: Settings) -> Dispatcher:
    """Собрать диспетчер с роутерами.

    Args:
        settings: Настройки приложения.

    Returns:
        Dispatcher: Инициализированный диспетчер.
    """
    service_factory = TelegramServiceFactory(settings.backend)
    user_settings_service = UserSettingsService()
    message_handler = MessageHandler(service_factory, user_settings_service)
    media_handler = MediaHandler(service_factory, user_settings_service)

    dispatcher = Dispatcher()
    dispatcher.include_router(message_handler.router)
    dispatcher.include_router(media_handler.router)
    return dispatcher


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управлять жизненным циклом webhook приложения.

    Args:
        app: Экземпляр FastAPI.

    Yields:
        None: Контроль жизненного цикла.
    """
    settings = get_settings()
    configure_logging(settings.app.log_level)
    bot = Bot(token=settings.bot.token)
    dispatcher = build_dispatcher(settings)
    logger.info("bot_service_starting")

    try:
        await bot.set_webhook(
            url=settings.bot.webhook_url,
            secret_token=settings.bot.webhook_secret,
        )
        await bot.set_my_commands(
            commands=[
                BotCommand(command="start", description="О боте и базе знаний"),
                BotCommand(command="settings", description="Настройки поиска и сохранения"),
                BotCommand(command="save", description="Сохранить текст в базу знаний"),
                BotCommand(command="help", description="Показать справку"),
            ]
        )
    except TelegramAPIError as error:
        logger.warning("Failed to set webhook: %s", error)

    app.state.bot = bot
    app.state.dispatcher = dispatcher
    app.state.settings = settings
    logger.info("bot_service_started")
    yield
    await bot.delete_webhook(drop_pending_updates=False)
    await bot.session.close()
    logger.info("bot_service_stopped")


app = FastAPI(title="bot-telegram", lifespan=lifespan)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health() -> dict[str, str]:
    """Проверить доступность bot-сервиса.

    Returns:
        dict[str, str]: Статус bot-сервиса.
    """
    return {"status": "ok", "service": "bot-telegram"}


@app.post("/webhook/telegram", status_code=status.HTTP_200_OK)
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(default=""),
) -> dict[str, bool]:
    """Принять webhook update и передать его в aiogram dispatcher.

    Args:
        request: Текущий HTTP запрос.
        x_telegram_bot_api_secret_token: Секретный токен webhook.

    Raises:
        HTTPException: Если секрет webhook неверный.

    Returns:
        dict[str, bool]: Признак успешной обработки.
    """
    settings = request.app.state.settings
    if x_telegram_bot_api_secret_token != settings.bot.webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook token"
        )

    payload = await request.json()
    update = Update.model_validate(payload)
    bot: Bot = request.app.state.bot
    dispatcher: Dispatcher = request.app.state.dispatcher
    await dispatcher.feed_update(bot, update)
    return {"ok": True}
