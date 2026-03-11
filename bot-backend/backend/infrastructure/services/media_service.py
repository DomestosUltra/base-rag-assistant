import base64

from openai import AsyncOpenAI

from backend.core.config import OpenAISettings


class MediaService:
    """Сервис работы с аудио и изображениями."""

    def __init__(self, settings: OpenAISettings) -> None:
        self._settings = settings
        self._client = AsyncOpenAI(api_key=settings.api_key, base_url=settings.base_url)

    async def transcribe_audio(
        self,
        content: bytes,
        file_name: str,
        content_type: str,
    ) -> str:
        """Транскрибировать аудиофайл в текст.

        Args:
            content: Содержимое аудиофайла.
            file_name: Имя файла.
            content_type: MIME тип файла.

        Returns:
            str: Транскрибированный текст.
        """
        transcript = await self._client.audio.transcriptions.create(
            model=self._settings.audio_model,
            file=(file_name, content, content_type),
        )
        return transcript.text

    async def describe_image(self, content: bytes) -> str:
        """Распознать содержание изображения.

        Args:
            content: Бинарное содержимое изображения.

        Returns:
            str: Текстовое описание изображения.
        """
        encoded = base64.b64encode(content).decode("utf-8")
        completion = await self._client.chat.completions.create(
            model=self._settings.vision_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Опиши изображение кратко и по фактам."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                        },
                    ],
                }
            ],
        )
        return completion.choices[0].message.content or ""
