import logging
import time

from redis.asyncio import Redis, ConnectionPool
from sqlalchemy import text

from bot.database import get_repo
from bot.settings import settings

logger = logging.getLogger(__name__)


async def test_redis_pool() -> None:
    redis_pool: Redis = Redis(
        connection_pool=ConnectionPool(
            host=settings.redis.ip,
            port=settings.redis.port,
            password=settings.redis.password,
        ),
    )

    try:
        server = await redis_pool.info("server")
    finally:
        await redis_pool.aclose()

    logger.debug("Successful connected to Redis(%s).", server["redis_version"])


async def test_database_pool() -> None:
    async with get_repo() as repo:
        start = time.perf_counter()
        info = (await repo.session.execute(text("SELECT version();"))).scalar()
        ping_ms = round((time.perf_counter() - start) * 1000, 3)

        if isinstance(info, str):
            version = info.split()[1]
        else:
            version = "unknown"

        logger.debug("Successful connected to %s(%s). Ping: %s ms", settings.db.used, version, ping_ms)
