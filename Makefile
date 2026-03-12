all:
	cd bot-backend && uv run ruff check . && uv run ruff format --check . && uv run mypy backend
	cd bot-backend && (uv run pytest || test $$? -eq 5)
	cd bot-telegram && uv run ruff check . && uv run ruff format --check . && uv run mypy bot

up:
	docker compose up --build -d

down:
	docker compose down -v

logs:
	docker compose logs -f

backend-shell:
	docker compose exec backend sh

bot-shell:
	docker compose exec bot sh

migrate:
	docker compose exec backend uv run alembic upgrade head
