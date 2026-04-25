from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
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
    app: str
    version: str
    environment: str
    uptime_seconds: float


STARTED_AT = time.monotonic()


def _health_response(status: Literal["ok", "degraded"], checks: dict[str, str]) -> HealthResponse:
    return HealthResponse(
        status=status,
        checks=checks,
        app=settings.app.name,
        version=settings.app.version,
        environment=settings.app.environment,
        uptime_seconds=round(time.monotonic() - STARTED_AT, 3),
    )


async def _run_check(name: str, check: Callable[[], Awaitable[str]]) -> tuple[str, str]:
    try:
        result = await asyncio.wait_for(check(), timeout=settings.healthcheck.timeout_seconds)
    except TimeoutError:
        return name, "error: TimeoutError"

    return name, result


async def _check_database() -> str:
    try:
        async with sessionmaker() as session:
            await session.execute(text("SELECT 1"))
    except (OSError, SQLAlchemyError) as error:
        return f"error: {error.__class__.__name__}"

    return "ok"


async def _check_redis() -> str:
    if not settings.redis.use:
        return "disabled"

    redis = settings.redis.get_redis()
    try:
        await redis.ping()
    except (OSError, RedisError) as error:
        return f"error: {error.__class__.__name__}"
    finally:
        await redis.aclose()

    return "ok"


async def _collect_readiness_checks() -> dict[str, str]:
    checks = await asyncio.gather(
        _run_check("database", _check_database),
        _run_check("redis", _check_redis),
    )
    return dict(checks)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app.name, version=settings.app.version)

    @app.get("/health/live", tags=["health"])
    async def live() -> HealthResponse:
        return _health_response(status="ok", checks={"app": "ok"})

    @app.get("/health/ready", tags=["health"])
    async def ready(response: Response) -> HealthResponse:
        checks = await _collect_readiness_checks()

        if any(check.startswith("error:") for check in checks.values()):
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return _health_response(status="degraded", checks=checks)

        return _health_response(status="ok", checks=checks)

    return app


app = create_app()
