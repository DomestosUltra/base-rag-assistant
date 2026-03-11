from aiogram.types import Message

from bot.dto.message import TelegramMessageDTO


class MessageAdapter:
    """Адаптер Telegram Message в DTO backend запроса."""

    def to_message_dto(self, message: Message) -> TelegramMessageDTO:
        """Преобразовать сообщение Telegram в DTO.

        Args:
            message: Сообщение Telegram.

        Returns:
            TelegramMessageDTO: Подготовленный DTO.
        """
        user_id = str(message.from_user.id) if message.from_user else "unknown"
        text = message.text or ""
        return TelegramMessageDTO(user_id=user_id, text=text)
