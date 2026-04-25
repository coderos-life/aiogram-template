from bot.enums.db import Databases
from bot.settings import DatabaseSettings, RedisSettings


def test_database_url_escapes_credentials() -> None:
    settings = DatabaseSettings(
        used=Databases.PostgreSQL,
        ip="postgres",
        port=5432,
        user="bot",
        password="p@ss/word",
        name="telegram_bot",
    )

    assert settings.build_postgres_url() == "postgresql+asyncpg://bot:p%40ss%2Fword@postgres:5432/telegram_bot"


def test_redis_password_can_be_disabled() -> None:
    settings = RedisSettings(use=False, ip="redis", port=6379, password=None)

    assert settings.password is None
