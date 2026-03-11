# Base RAG Assistant

Проект состоит из двух микросервисов:
- `bot-backend` — FastAPI backend с RAG на LangChain + OpenAI + Weaviate.
- `bot-telegram` — Telegram-бот на Aiogram 3, который обращается к backend по REST.

## Быстрый старт

1. Скопируйте `.env.example` в `.env`.
2. Заполните `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `BACKEND_API_KEY`, `BOT_TOKEN`.
3. Запустите `make up`.
4. Backend будет доступен на `http://localhost:8000`.

## Основные команды

- `make up`
- `make down`
- `make logs`
- `make migrate`
- `make all`
