"""Configuration for integrational tests."""

import pytest
import pytest_asyncio
from asyncpg import PostgresError
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import Repositories
from bot.database.models import Base
from bot.settings import settings
from tests.utils.mocked_bot import MockedBot

if settings.db.test_name:
    settings.db.name = settings.db.test_name


from bot.database.engine import engine, sessionmaker


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def clear_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database() -> None:
    try:
        await create_tables()
    except (OSError, PostgresError, SQLAlchemyError) as error:
        pytest.skip(f"PostgreSQL is not available for integration tests: {error}")

    yield

    await clear_tables()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def reset_database(prepare_database: None) -> None:
    await create_tables()
    yield
    await clear_tables()


@pytest_asyncio.fixture(scope="function")
async def session() -> AsyncSession:
    async with sessionmaker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def repo(session: AsyncSession):
    """Database fixture."""
    repo = Repositories.get_repo(session)

    yield repo


@pytest.fixture()
def bot() -> MockedBot:
    """Bot fixture."""
    return MockedBot()


@pytest.fixture()
def storage() -> MemoryStorage:
    """Storage fixture."""
    return MemoryStorage()


@pytest.fixture()
def dp(storage) -> Dispatcher:
    """Dispatcher fixture."""
    return Dispatcher(storage=storage)
