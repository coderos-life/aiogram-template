from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from bot.database.engine import sessionmaker
from bot.settings import settings


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    checks: dict[str, str]


async def _check_database() -> str:
    try:
        async with sessionmaker() as session:
            await session.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        return f"error: {error.__class__.__name__}"

    return "ok"


async def _check_redis() -> str:
    if not settings.redis.use:
        return "disabled"

    redis = settings.redis.get_redis()
    try:
        await redis.ping()
    except RedisError as error:
        return f"error: {error.__class__.__name__}"
    finally:
        await redis.aclose()

    return "ok"


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app.name, version="0.1.0")

    @app.get("/health/live", tags=["health"])
    async def live() -> HealthResponse:
        return HealthResponse(status="ok", checks={"app": "ok"})

    @app.get("/health/ready", tags=["health"])
    async def ready(response: Response) -> HealthResponse:
        checks = {
            "database": await _check_database(),
            "redis": await _check_redis(),
        }

        if any(check.startswith("error:") for check in checks.values()):
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return HealthResponse(status="degraded", checks=checks)

        return HealthResponse(status="ok", checks=checks)

    return app


app = create_app()
