import logging
from importlib import import_module
from io import BytesIO
from pathlib import Path
from typing import Any

from aiogram import F, Router
from aiogram.types import Message

from bot.dto.message import (
    TelegramKnowledgeMetadataDTO,
    TelegramKnowledgeSaveTextDTO,
    TelegramPhotoDTO,
    TelegramVoiceDTO,
)
from bot.factories.service_factory import TelegramServiceFactory
from bot.services.user_settings_service import UserSettingsService

logger = logging.getLogger(__name__)


class MediaHandler:
    """Временный обработчик медиа событий Telegram."""

    def __init__(
        self,
        service_factory: TelegramServiceFactory,
        user_settings_service: UserSettingsService,
    ) -> None:
        self._service_factory = service_factory
        self._user_settings_service = user_settings_service
        self.router = Router()
        self.router.message.register(self._handle_voice, F.voice)
        self.router.message.register(self._handle_photo, F.photo)
        self.router.message.register(self._handle_document, F.document)

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

    async def _handle_voice(self, message: Message) -> None:
        """Обработать голосовое сообщение.

        Args:
            message: Сообщение Telegram.
        """
        user_id = str(message.from_user.id) if message.from_user else "unknown"
        settings = self._user_settings_service.get(user_id)
        logger.info(
            "telegram_action=voice_received user_id=%s chat_id=%s message_id=%s",
            user_id,
            message.chat.id,
            message.message_id,
        )
        processing_message = await message.answer("🎙️ Обрабатываю голосовое сообщение...")
        voice = message.voice
        if voice is None:
            logger.info(
                "telegram_action=voice_rejected_missing user_id=%s chat_id=%s message_id=%s",
                user_id,
                message.chat.id,
                message.message_id,
            )
            await self._finalize_processing_message(
                processing_message,
                "⚠️ Голосовое сообщение не найдено.",
            )
            return

        try:
            bot = message.bot
            if bot is None:
                raise RuntimeError("Telegram bot instance is not available")
            file_info = await bot.get_file(voice.file_id)
            if not file_info.file_path:
                raise RuntimeError("Telegram file path is empty")
            file_bytes = await bot.download_file(file_info.file_path)
            if file_bytes is None:
                raise RuntimeError("Telegram file bytes are empty")
            audio_bytes = file_bytes.read()
        except Exception as error:
            logger.exception("Failed to download Telegram voice: %s", error)
            await self._finalize_processing_message(
                processing_message,
                "⚠️ Не удалось загрузить голосовое сообщение.",
            )
            return

        payload = TelegramVoiceDTO(
            user_id=user_id,
            audio_bytes=audio_bytes,
            file_name=f"voice_{voice.file_unique_id}.ogg",
            content_type="audio/ogg",
        )

        try:
            answer = await self._service_factory.ask_voice(
                payload,
                search_shared=settings.search_shared,
            )
            logger.info(
                "telegram_action=voice_answer_success user_id=%s chat_id=%s message_id=%s answer_len=%s",
                user_id,
                message.chat.id,
                message.message_id,
                len(answer),
            )
            await self._finalize_processing_message(processing_message, answer)
        except Exception as error:
            logger.exception(
                "telegram_action=voice_answer_failed user_id=%s chat_id=%s message_id=%s error=%s",
                user_id,
                message.chat.id,
                message.message_id,
                error,
            )
            await self._finalize_processing_message(
                processing_message,
                "⚠️ Не удалось обработать голосовое сообщение.\nПопробуй отправить его ещё раз.",
            )

    async def _handle_photo(self, message: Message) -> None:
        """Обработать сообщение с изображением.

        Args:
            message: Сообщение Telegram.
        """
        user_id = str(message.from_user.id) if message.from_user else "unknown"
        settings = self._user_settings_service.get(user_id)
        logger.info(
            "telegram_action=photo_received user_id=%s chat_id=%s message_id=%s has_caption=%s",
            user_id,
            message.chat.id,
            message.message_id,
            bool(message.caption),
        )
        processing_message = await message.answer("🖼️ Анализирую изображение...")
        photos = message.photo or []
        if not photos:
            logger.info(
                "telegram_action=photo_rejected_missing user_id=%s chat_id=%s message_id=%s",
                user_id,
                message.chat.id,
                message.message_id,
            )
            await self._finalize_processing_message(
                processing_message,
                "⚠️ Изображение не найдено.",
            )
            return

        largest_photo = photos[-1]
        try:
            bot = message.bot
            if bot is None:
                raise RuntimeError("Telegram bot instance is not available")
            file_info = await bot.get_file(largest_photo.file_id)
            if not file_info.file_path:
                raise RuntimeError("Telegram file path is empty")
            file_bytes = await bot.download_file(file_info.file_path)
            if file_bytes is None:
                raise RuntimeError("Telegram file bytes are empty")
            image_bytes = file_bytes.read()
        except Exception as error:
            logger.exception("Failed to download Telegram photo: %s", error)
            await self._finalize_processing_message(
                processing_message,
                "⚠️ Не удалось загрузить изображение.",
            )
            return

        prompt = (message.caption or "").strip() or "Что на картинке?"
        payload = TelegramPhotoDTO(
            user_id=user_id,
            text=prompt,
            image_bytes=image_bytes,
            file_name=f"photo_{largest_photo.file_unique_id}.jpg",
            content_type="image/jpeg",
        )

        try:
            answer = await self._service_factory.ask_photo(
                payload,
                search_shared=settings.search_shared,
            )
            logger.info(
                "telegram_action=photo_answer_success user_id=%s chat_id=%s message_id=%s prompt_len=%s answer_len=%s",
                user_id,
                message.chat.id,
                message.message_id,
                len(prompt),
                len(answer),
            )
            await self._finalize_processing_message(processing_message, answer)
        except Exception as error:
            logger.exception(
                "telegram_action=photo_answer_failed user_id=%s chat_id=%s message_id=%s error=%s",
                user_id,
                message.chat.id,
                message.message_id,
                error,
            )
            await self._finalize_processing_message(
                processing_message,
                "⚠️ Не удалось обработать изображение.\nПопробуй отправить фото ещё раз.",
            )

    async def _handle_document(self, message: Message) -> None:
        """Обработать документ и сохранить текст в базу знаний.

        Args:
            message: Сообщение Telegram.
        """
        document = message.document
        user_id = str(message.from_user.id) if message.from_user else "unknown"
        settings = self._user_settings_service.get(user_id)
        scope_text = "общую" if settings.save_scope == "shared" else "персональную"
        logger.info(
            "telegram_action=document_received user_id=%s chat_id=%s message_id=%s file_name=%s",
            user_id,
            message.chat.id,
            message.message_id,
            document.file_name if document else "",
        )
        if document is None:
            logger.info(
                "telegram_action=document_rejected_missing user_id=%s chat_id=%s message_id=%s",
                user_id,
                message.chat.id,
                message.message_id,
            )
            await message.answer("⚠️ Документ не найден в сообщении.")
            return

        processing_message = await message.answer(
            f"📄 Если формат файла поддерживается, сохраню его в {scope_text} базу знаний..."
        )

        file_name = document.file_name or "document"
        suffix = Path(file_name).suffix.lower()
        mime_type = (document.mime_type or "").lower()
        supported_suffixes = {
            ".txt",
            ".md",
            ".markdown",
            ".csv",
            ".json",
            ".log",
            ".rst",
            ".docx",
        }
        supported_mime_types = {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        if not (
            mime_type.startswith("text/")
            or mime_type in supported_mime_types
            or suffix in supported_suffixes
        ):
            logger.info(
                "telegram_action=document_rejected_type user_id=%s chat_id=%s message_id=%s mime_type=%s suffix=%s",
                user_id,
                message.chat.id,
                message.message_id,
                mime_type,
                suffix,
            )
            await self._finalize_processing_message(
                processing_message,
                "⚠️ Этот формат не поддерживается.\n"
                "Поддерживаются файлы, которые сохраняются в базу: txt, md, csv, json, log, rst, docx.",
            )
            return

        try:
            bot = message.bot
            if bot is None:
                raise RuntimeError("Telegram bot instance is not available")
            file_info = await bot.get_file(document.file_id)
            if not file_info.file_path:
                raise RuntimeError("Telegram file path is empty")
            file_bytes = await bot.download_file(file_info.file_path)
            if file_bytes is None:
                raise RuntimeError("Telegram file bytes are empty")
            content_bytes = file_bytes.read()
            text = self._extract_text_from_document(
                content_bytes=content_bytes,
                suffix=suffix,
            ).strip()
        except Exception as error:
            logger.exception("Failed to download Telegram file: %s", error)
            await self._finalize_processing_message(
                processing_message,
                "⚠️ Не удалось загрузить файл из Telegram.",
            )
            return

        if not text:
            logger.info(
                "telegram_action=document_rejected_empty user_id=%s chat_id=%s message_id=%s file_name=%s",
                user_id,
                message.chat.id,
                message.message_id,
                file_name,
            )
            await self._finalize_processing_message(
                processing_message,
                "⚠️ Файл пустой или не содержит читаемого текста.",
            )
            return

        metadata = TelegramKnowledgeMetadataDTO(
            title=file_name,
            source="telegram",
            source_type="telegram_file",
            author=str(message.from_user.id) if message.from_user else None,
            external_id=document.file_unique_id,
            collection_scope=settings.save_scope,
            tags=["telegram", "file", suffix.lstrip(".") or "text", settings.save_scope],
        )
        payload = TelegramKnowledgeSaveTextDTO(user_id=user_id, text=text, metadata=metadata)

        try:
            saved_chunks = await self._service_factory.save_knowledge_text(payload)
            logger.info(
                "telegram_action=document_save_success user_id=%s chat_id=%s message_id=%s file_name=%s saved_chunks=%s",
                user_id,
                message.chat.id,
                message.message_id,
                file_name,
                saved_chunks,
            )
            await self._finalize_processing_message(
                processing_message,
                f"✅ Файл сохранён в {scope_text} базу знаний.\nЧанков: {saved_chunks}",
            )
        except Exception as error:
            logger.exception(
                "telegram_action=document_save_failed user_id=%s chat_id=%s message_id=%s file_name=%s error=%s",
                user_id,
                message.chat.id,
                message.message_id,
                file_name,
                error,
            )
            await self._finalize_processing_message(
                processing_message,
                "⚠️ Не удалось сохранить файл в базу знаний.\nПопробуй ещё раз позже.",
            )

    @staticmethod
    def _extract_text_from_docx(content_bytes: bytes) -> str:
        """Извлечь текст из DOCX файла.

        Args:
            content_bytes: Бинарное содержимое файла.

        Returns:
            str: Текст документа.
        """
        docx_module: Any = import_module("docx")
        document = docx_module.Document(BytesIO(content_bytes))
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        return "\n".join(paragraphs)

    def _extract_text_from_document(self, content_bytes: bytes, suffix: str) -> str:
        """Извлечь текст из поддерживаемого файла.

        Args:
            content_bytes: Бинарное содержимое файла.
            suffix: Расширение файла.

        Returns:
            str: Текст файла.
        """
        if suffix == ".docx":
            return self._extract_text_from_docx(content_bytes)
        return content_bytes.decode("utf-8", errors="ignore")
