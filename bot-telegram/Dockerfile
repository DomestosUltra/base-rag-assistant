FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml /app/pyproject.toml
RUN uv sync --frozen || uv sync

COPY . /app

CMD ["uv", "run", "uvicorn", "bot.main:app", "--host", "0.0.0.0", "--port", "8081"]
