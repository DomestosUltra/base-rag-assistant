from contextlib import asynccontextmanager
from time import perf_counter
from collections.abc import Awaitable, Callable
from typing import AsyncGenerator

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request, Response
from prometheus_fastapi_instrumentator import Instrumentator

from backend.api.v1.router import router as v1_router
from backend.core.config import get_settings
from backend.core.exceptions import CustomException, custom_exception_handler
from backend.core.logging import configure_logging, get_logger
from backend.infrastructure.di.container import create_container
from backend.infrastructure.vectorstore.weaviate_store import WeaviateKnowledgeStore

logger = get_logger(__name__)
container = create_container()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управлять жизненным циклом приложения.

    Args:
        app: Экземпляр FastAPI.

    Yields:
        None: Управление выполнением приложения.
    """
    settings = get_settings()
    configure_logging(settings.app.log_level)
    await container.get(WeaviateKnowledgeStore)
    logger.info("Backend service started")
    yield
    await container.close()
    logger.info("Backend service stopped")


app = FastAPI(title="bot-backend", lifespan=lifespan)
app.add_exception_handler(CustomException, custom_exception_handler)


@app.middleware("http")
async def log_http_requests(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Логировать входящие HTTP запросы и их результат."""
    started_at = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        logger.exception(
            "http_request_failed",
            method=request.method,
            path=request.url.path,
            duration_ms=duration_ms,
        )
        raise

    duration_ms = round((perf_counter() - started_at) * 1000, 2)
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )
    return response


app.include_router(v1_router)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
setup_dishka(container=container, app=app)
