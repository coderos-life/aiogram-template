import asyncio
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from asyncpg import PostgresError
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from bot.database.engine import engine
from bot.database.models import Base
from bot.settings import settings


PROJECT_DIR = Path(__file__).resolve().parents[2]


def make_alembic_config() -> Config:
    return Config(str(PROJECT_DIR / "alembic.ini"))


async def drop_database_schema() -> None:
    if settings.app.environment != "test":
        pytest.skip("Alembic integration test can only run against APP_ENVIRONMENT=test.")

    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
    except (OSError, PostgresError, SQLAlchemyError) as error:
        pytest.skip(f"PostgreSQL is not available for Alembic integration tests: {error}")


async def get_table_names() -> set[str]:
    async with engine.connect() as connection:
        return await connection.run_sync(lambda sync_connection: set(inspect(sync_connection).get_table_names()))


async def get_current_revision() -> str:
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT version_num FROM alembic_version"))
        return result.scalar_one()


@pytest.mark.integration
async def test_alembic_upgrade_head_creates_current_schema() -> None:
    await drop_database_schema()

    try:
        await asyncio.to_thread(command.upgrade, make_alembic_config(), "head")

        tables = await get_table_names()

        assert {"users", "chats", "alembic_version"} <= tables
        assert await get_current_revision() == "001"

        await asyncio.to_thread(command.downgrade, make_alembic_config(), "base")

        tables = await get_table_names()
        assert "users" not in tables
        assert "chats" not in tables
    finally:
        await drop_database_schema()
