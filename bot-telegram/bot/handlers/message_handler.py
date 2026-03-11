import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.adapters.message_adapter import MessageAdapter
from bot.dto.message import (
    TelegramKnowledgeMetadataDTO,
    TelegramKnowledgeSaveTextDTO,
    TelegramUserSettingsDTO,
)
from bot.factories.service_factory import TelegramServiceFactory
from bot.services.user_settings_service import UserSettingsService

logger = logging.getLogger(__name__)


class MessageHandler:
    """Обработчик текстовых сообщений Telegram."""

    def __init__(
        self,
        service_factory: TelegramServiceFactory,
        user_settings_service: UserSettingsService,
    ) -> None:
        self._service_factory = service_factory
        self._user_settings_service = user_settings_service
        self._adapter = MessageAdapter()
        self.router = Router()
        self.router.message.register(self._handle_start, Command("start"))
        self.router.message.register(self._handle_settings, Command("settings"))
        self.router.message.register(self._handle_help, Command("help"))
        self.router.message.register(self._handle_save_text, Command("save"))
        self.router.callback_query.register(
            self._handle_settings_callback,
            lambda callback: bool(callback.data and callback.data.startswith("settings:")),
        )
        self.router.message.register(self._handle_text, F.text)

    def _build_settings_keyboard(self, settings: TelegramUserSettingsDTO) -> InlineKeyboardMarkup:
        """Построить inline-клавиатуру пользовательских настроек.

        Args:
            settings: Текущие настройки пользователя.

        Returns:
            InlineKeyboardMarkup: Клавиатура настроек.
        """
        next_scope = "personal" if settings.save_scope == "shared" else "shared"
        save_scope_text = "общая" if settings.save_scope == "shared" else "персональная"
        search_shared_text = "вкл" if settings.search_shared else "выкл"
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"Сохранять: {save_scope_text}",
                        callback_data=f"settings:save_scope:{next_scope}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=f"Искать по общим данным: {search_shared_text}",
                        callback_data="settings:toggle_search_shared",
                    )
                ],
            ]
        )

    def _build_settings_text(self, settings: TelegramUserSettingsDTO) -> str:
        """Сформировать текст экрана пользовательских настроек.

        Args:
            settings: Текущие настройки пользователя.

        Returns:
            str: Текст настроек.
        """
        save_scope_text = "Общая коллекция" if settings.save_scope == "shared" else "Персональная коллекция"
        search_mode_text = (
            "Общие + персональные данные"
            if settings.search_shared
            else "Только персональные данные"
        )
        return (
            "⚙️ Настройки поиска и сохранения\n\n"
            f"• Сохранение: {save_scope_text}\n"
            f"• Поиск: {search_mode_text}\n\n"
            "ℹ️ В общей коллекции данные доступны всем пользователям."
        )

    async def _handle_start(self, message: Message) -> None:
        """Показать приветствие и правила работы с базой знаний.

        Args:
            message: Сообщение Telegram.
        """
        user_id = str(message.from_user.id) if message.from_user else "unknown"
        logger.info(
            "telegram_action=start user_id=%s chat_id=%s message_id=%s",
            user_id,
            message.chat.id,
            message.message_id,
        )
        start_text = (
            "👋 Привет! Я бот с общей базой знаний.\n\n"
            "ℹ️ База общая для всех пользователей:\n"
            "каждый может находить данные, сохранённые другими, и наоборот.\n\n"
            "Команды:\n"
            "• /settings — настройки поиска и сохранения\n"
            "• /save <текст> — сохранить текст в базу\n"
            "• /help — справка\n\n"
            "💬 Просто отправь вопрос текстом, голосом или фото."
        )
        await message.answer(start_text)

    async def _handle_settings(self, message: Message) -> None:
        """Показать экран пользовательских настроек.

        Args:
            message: Сообщение Telegram.
        """
        user_id = str(message.from_user.id) if message.from_user else "unknown"
        logger.info(
            "telegram_action=settings_open user_id=%s chat_id=%s message_id=%s",
            user_id,
            message.chat.id,
            message.message_id,
        )
        settings = self._user_settings_service.get(user_id)
        await message.answer(
            self._build_settings_text(settings),
            reply_markup=self._build_settings_keyboard(settings),
        )

    async def _handle_settings_callback(self, callback: CallbackQuery) -> None:
        """Обработать нажатия inline-кнопок настроек.

        Args:
            callback: CallbackQuery Telegram.
        """
        if callback.data is None:
            await callback.answer("Некорректный callback", show_alert=False)
            return
        if callback.from_user is None:
            await callback.answer("Пользователь не определен", show_alert=False)
            return

        user_id = str(callback.from_user.id)
        settings = self._user_settings_service.get(user_id)

        if callback.data.startswith("settings:save_scope:"):
            scope = callback.data.split(":")[-1]
            if scope in {"shared", "personal"}:
                settings = self._user_settings_service.set_save_scope(user_id, scope)
        elif callback.data == "settings:toggle_search_shared":
            settings = self._user_settings_service.toggle_search_shared(user_id)

        logger.info(
            "telegram_action=settings_updated user_id=%s chat_id=%s callback_data=%s save_scope=%s search_shared=%s",
            user_id,
            callback.message.chat.id if callback.message else "unknown",
            callback.data,
            settings.save_scope,
            settings.search_shared,
        )

        if callback.message is not None:
            await callback.message.edit_text(
                self._build_settings_text(settings),
                reply_markup=self._build_settings_keyboard(settings),
            )
        await callback.answer("Настройки обновлены", show_alert=False)

    async def _handle_help(self, message: Message) -> None:
        """Показать список доступных команд.

        Args:
            message: Сообщение Telegram.
        """
        user_id = str(message.from_user.id) if message.from_user else "unknown"
        logger.info(
            "telegram_action=help user_id=%s chat_id=%s message_id=%s",
            user_id,
            message.chat.id,
            message.message_id,
        )
        help_text = (
            "✨ Что я умею:\n\n"
            "• /settings — настройки поиска и сохранения\n"
            "• /save <текст> — сохранить текст в базу знаний\n"
            "• /help — показать эту справку\n\n"
            "ℹ️ Это общая база знаний: ты можешь найти данные других пользователей,\n"
            "а они — твои.\n\n"
            "💡 Просто отправь сообщение, и я отвечу."
        )
        await message.answer(help_text)

    async def _finalize_processing_message(self, processing_message: Message, text: str) -> None:
        """Обновить сообщение-заглушку финальным результатом.

        Args:
            processing_message: Сообщение-заглушка.
            text: Финальный текст ответа.
        """
        try:
            await processing_message.edit_text(text)
        except Exception:
            await processing_message.answer(text)

    async def _handle_save_text(self, message: Message) -> None:
        """Сохранить текст из команды /save в базу знаний.

        Args:
            message: Сообщение Telegram.
        """
        user_id = str(message.from_user.id) if message.from_user else "unknown"
        text = (message.text or "").strip()
        content = text[5:].strip() if text.startswith("/save") else ""
        settings = self._user_settings_service.get(user_id)
        scope_text = "общую" if settings.save_scope == "shared" else "персональную"
        logger.info(
            "telegram_action=save_text_received user_id=%s chat_id=%s message_id=%s content_len=%s",
            user_id,
            message.chat.id,
            message.message_id,
            len(content),
        )
        if not content:
            logger.info(
                "telegram_action=save_text_rejected_empty user_id=%s chat_id=%s message_id=%s",
                user_id,
                message.chat.id,
                message.message_id,
            )
            await message.answer(
                "📝 Добавь текст после команды.\n"
                f"⚠️ Важно: текст сохраняется в {scope_text} базу знаний.\n"
                "Пример: /save Важная информация для базы знаний"
            )
            return

        processing_message = await message.answer(f"⏳ Сохраняю текст в {scope_text} базу знаний...")

        metadata = TelegramKnowledgeMetadataDTO(
            title=content[:80],
            source="telegram",
            source_type="telegram_text",
            author=str(message.from_user.id) if message.from_user else None,
            external_id=str(message.message_id),
            collection_scope=settings.save_scope,
            tags=["telegram", "text", settings.save_scope],
        )
        payload = TelegramKnowledgeSaveTextDTO(user_id=user_id, text=content, metadata=metadata)

        try:
            saved_chunks = await self._service_factory.save_knowledge_text(payload)
            logger.info(
                "telegram_action=save_text_success user_id=%s chat_id=%s message_id=%s saved_chunks=%s",
                user_id,
                message.chat.id,
                message.message_id,
                saved_chunks,
            )
            await self._finalize_processing_message(
                processing_message,
                f"✅ Текст сохранён в {scope_text} базу знаний.\n"
                f"Чанков: {saved_chunks}",
            )
        except Exception as error:
            logger.exception(
                "telegram_action=save_text_failed user_id=%s chat_id=%s message_id=%s error=%s",
                user_id,
                message.chat.id,
                message.message_id,
                error,
            )
            await self._finalize_processing_message(
                processing_message,
                "⚠️ Не удалось сохранить текст в базу знаний.\nПопробуй ещё раз чуть позже.",
            )

    async def _handle_text(self, message: Message) -> None:
        """Обработать текстовое сообщение пользователя.

        Args:
            message: Сообщение Telegram.
        """
        if (message.text or "").strip().startswith("/"):
            logger.info(
                "telegram_action=command_skipped_from_search user_id=%s chat_id=%s message_id=%s command=%s",
                str(message.from_user.id) if message.from_user else "unknown",
                message.chat.id,
                message.message_id,
                (message.text or "").strip(),
            )
            return
        user_id = str(message.from_user.id) if message.from_user else "unknown"
        logger.info(
            "telegram_action=text_received user_id=%s chat_id=%s message_id=%s text_len=%s",
            user_id,
            message.chat.id,
            message.message_id,
            len(message.text or ""),
        )
        settings = self._user_settings_service.get(user_id)
        processing_message = await message.answer("⏳ Думаю над ответом...")
        payload = self._adapter.to_message_dto(message)
        try:
            answer = await self._service_factory.ask_text(
                payload,
                search_shared=settings.search_shared,
            )
            logger.info(
                "telegram_action=text_answer_success user_id=%s chat_id=%s message_id=%s answer_len=%s",
                user_id,
                message.chat.id,
                message.message_id,
                len(answer),
            )
            await self._finalize_processing_message(processing_message, answer)
        except Exception as error:
            logger.exception(
                "telegram_action=text_answer_failed user_id=%s chat_id=%s message_id=%s error=%s",
                user_id,
                message.chat.id,
                message.message_id,
                error,
            )
            await self._finalize_processing_message(
                processing_message,
                "⚠️ Сервис временно недоступен.\nПопробуй ещё раз через минуту.",
            )
