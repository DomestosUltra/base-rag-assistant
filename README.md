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

## CI/CD (GitHub Actions → Server)

Workflow: `.github/workflows/ci-cd.yml`

Триггер:
- push в ветку `stage`
- ручной запуск (`workflow_dispatch`)

Pipeline:
- CI: `ruff` + `mypy` для `bot-backend` и `bot-telegram`
- Build: сборка Docker-образов и push в `ghcr.io`
- CD: деплой по SSH на сервер, `docker compose pull && up -d` (без сборки на сервере)

Нужные GitHub Secrets:
- `SSH_HOST` — IP/домен сервера (например, `83.166.244.106`)
- `SSH_PORT` — SSH порт (обычно `22`)
- `SSH_USER` — пользователь SSH (например, `root`)
- `SSH_PRIVATE_KEY` — приватный ключ для SSH
- `APP_DIR` — путь к проекту на сервере (например, `/opt/base-rag-assistant`)
- `DEPLOY_BRANCH` — ветка деплоя (обычно `stage`)
- `REGISTRY_USERNAME` — логин для registry (для GHCR обычно GitHub username)
- `REGISTRY_PASSWORD` — токен для registry (для GHCR: PAT с правами чтения пакетов)

Требования на сервере:
- установлен `docker` + `docker compose`
- проект уже склонирован в `APP_DIR`
- `.env` заполнен в `APP_DIR`
- присутствует `docker-compose.registry.yml`
