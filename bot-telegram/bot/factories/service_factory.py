import asyncio
from typing import Any

import httpx

from bot.core.config import BackendSettings
from bot.dto.message import (
    TelegramKnowledgeSaveTextDTO,
    TelegramMessageDTO,
    TelegramPhotoDTO,
    TelegramVoiceDTO,
)


class TelegramServiceFactory:
    """Фабрика вызовов backend API из Telegram сервиса."""

    def __init__(self, backend: BackendSettings) -> None:
        self._backend = backend

    async def _request_with_retry(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Выполнить HTTP запрос к backend с коротким retry для сетевых сбоев.

        Args:
            client: HTTP клиент.
            method: HTTP метод.
            url: URL endpoint.
            **kwargs: Параметры запроса.

        Returns:
            httpx.Response: Ответ backend.

        Raises:
            httpx.HTTPError: Если все попытки завершились ошибкой.
        """
        last_error: httpx.HTTPError | None = None
        for attempt in range(3):
            try:
                return await client.request(method=method, url=url, **kwargs)
            except (httpx.ConnectError, httpx.TimeoutException) as error:
                last_error = error
                if attempt == 2:
                    break
                await asyncio.sleep(0.5 * (attempt + 1))

        if last_error is None:
            raise httpx.ConnectError("Unknown network error")
        raise last_error

    async def ask_text(self, payload: TelegramMessageDTO, search_shared: bool) -> str:
        """Отправить текстовый запрос в backend.

        Args:
            payload: DTO сообщения пользователя.

        Returns:
            str: Ответ ассистента.
        """
        headers = {
            "X-API-Key": self._backend.api_key,
            "X-User-Id": payload.user_id,
        }
        async with httpx.AsyncClient(base_url=self._backend.base_url, timeout=60.0) as client:
            response = await self._request_with_retry(
                client=client,
                method="POST",
                url="/v1/query/text-image",
                data={"text": payload.text, "search_shared": str(search_shared).lower()},
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            return str(data.get("answer", ""))

    async def save_knowledge_text(self, payload: TelegramKnowledgeSaveTextDTO) -> int:
        """Сохранить текст в базу знаний backend.

        Args:
            payload: DTO текста и metadata.

        Returns:
            int: Количество сохраненных чанков.
        """
        headers = {
            "X-API-Key": self._backend.api_key,
            "X-User-Id": payload.user_id,
        }
        async with httpx.AsyncClient(base_url=self._backend.base_url, timeout=60.0) as client:
            response = await self._request_with_retry(
                client=client,
                method="POST",
                url="/v1/knowledge/text",
                json=payload.model_dump(mode="json"),
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            return int(data.get("saved_chunks", 0))

    async def ask_voice(self, payload: TelegramVoiceDTO, search_shared: bool) -> str:
        """Отправить голосовой запрос в backend.

        Args:
            payload: DTO голосового сообщения.

        Returns:
            str: Ответ ассистента.
        """
        headers = {
            "X-API-Key": self._backend.api_key,
            "X-User-Id": payload.user_id,
        }
        files = {
            "audio": (
                payload.file_name,
                payload.audio_bytes,
                payload.content_type,
            )
        }
        async with httpx.AsyncClient(base_url=self._backend.base_url, timeout=120.0) as client:
            response = await self._request_with_retry(
                client=client,
                method="POST",
                url="/v1/query/audio-image",
                files=files,
                data={"search_shared": str(search_shared).lower()},
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            return str(data.get("answer", ""))

    async def ask_photo(self, payload: TelegramPhotoDTO, search_shared: bool) -> str:
        """Отправить изображение в multimodal endpoint backend.

        Args:
            payload: DTO изображения и текстового запроса.

        Returns:
            str: Ответ ассистента.
        """
        headers = {
            "X-API-Key": self._backend.api_key,
            "X-User-Id": payload.user_id,
        }
        files = {
            "image": (
                payload.file_name,
                payload.image_bytes,
                payload.content_type,
            )
        }
        async with httpx.AsyncClient(base_url=self._backend.base_url, timeout=120.0) as client:
            response = await self._request_with_retry(
                client=client,
                method="POST",
                url="/v1/query/text-image",
                data={"text": payload.text, "search_shared": str(search_shared).lower()},
                files=files,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            return str(data.get("answer", ""))
