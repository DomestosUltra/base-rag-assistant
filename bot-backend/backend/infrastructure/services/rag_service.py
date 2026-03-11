from langchain_openai import ChatOpenAI

from backend.core.config import OpenAISettings
from backend.domain.services.rag_service import RagService
from backend.infrastructure.vectorstore.weaviate_store import WeaviateKnowledgeStore


class RagServiceImpl(RagService):
    """RAG сервис для ответов на запросы пользователя."""

    def __init__(
        self,
        settings: OpenAISettings,
        knowledge_store: WeaviateKnowledgeStore,
    ) -> None:
        self._knowledge_store = knowledge_store
        self._model = ChatOpenAI(
            model=settings.chat_model,
            api_key=settings.api_key,
            base_url=settings.base_url,
        )

    async def ask(
        self,
        user_id: str,
        text: str,
        history_messages: list[str],
        image_context: str | None,
        request_type: str,
        search_shared: bool,
    ) -> str:
        """Сформировать ответ на основе контекста и базы знаний.

        Args:
            user_id: Идентификатор пользователя.
            text: Текст запроса.
            history_messages: История сообщений пользователя.
            image_context: Контекст изображения.
            request_type: Тип запроса.
            search_shared: Флаг поиска по общей базе знаний.

        Returns:
            str: Текст ответа.
        """
        context_docs = await self._knowledge_store.search(
            query=text,
            user_id=user_id,
            search_shared=search_shared,
            k=4,
        )
        context = "\n\n".join(context_docs)
        history = "\n".join(history_messages)
        image_part = image_context if image_context else ""
        prompt = (
            "Ты ИИ-консультант. Отвечай только по базе знаний и входным данным. "
            "Если данных недостаточно, так и напиши.\n"
            f"История:\n{history}\n"
            f"Контекст из базы:\n{context}\n"
            f"Контекст изображения:\n{image_part}\n"
            f"Тип запроса: {request_type}\n"
            f"Вопрос: {text}"
        )
        response = await self._model.ainvoke(prompt)
        answer = response.content if isinstance(response.content, str) else str(response.content)
        return answer
