from bot.enums.db import Databases
from bot.settings import DatabaseSettings, HealthcheckSettings, RedisSettings


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


def test_database_pool_settings_have_production_defaults() -> None:
    settings = DatabaseSettings(
        used=Databases.PostgreSQL,
        ip="postgres",
        port=5432,
        user="bot",
        password="postgres",
        name="telegram_bot",
    )

    assert settings.pool_size == 5
    assert settings.max_overflow == 10
    assert settings.pool_timeout == 30
    assert settings.pool_recycle == 1800


def test_redis_connection_uses_configured_db_and_timeouts() -> None:
    settings = RedisSettings(
        use=True,
        ip="redis",
        port=6379,
        db=2,
        password=None,
        socket_timeout=1.5,
        socket_connect_timeout=2.5,
    )

    redis = settings.get_redis()

    assert redis.connection_pool.connection_kwargs["db"] == 2
    assert redis.connection_pool.connection_kwargs["socket_timeout"] == 1.5
    assert redis.connection_pool.connection_kwargs["socket_connect_timeout"] == 2.5


def test_healthcheck_timeout_default_is_bounded() -> None:
    settings = HealthcheckSettings()

    assert settings.timeout_seconds == 3
