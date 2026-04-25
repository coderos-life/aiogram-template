from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from redis.asyncio import Redis
from sqlalchemy.engine import URL

from bot.enums.db import Databases, MySQLDrivers, PostgreSQLDrivers

load_dotenv(find_dotenv())

ProjectDir = Path(__file__).parent.parent
BotDir = ProjectDir / "bot"
LogDir = Path(ProjectDir) / "logs"


class AppSettings(BaseSettings):
    name: str = "Aiogram Bot Template"
    version: str = "0.1.0"
    environment: Literal["local", "development", "staging", "production", "test"] = "local"
    timezone: str = "Europe/Moscow"

    model_config = SettingsConfigDict(env_prefix="APP_")


class BotSettings(BaseSettings):
    bot_token: str
    parse_mode: Literal["MARKDOWN_V2", "MARKDOWN", "HTML"] = "HTML"
    drop_pending_updates: bool = True
    rate_limit: int | float = 1
    allowed_updates: list[str] | None = None


class DatabaseSettings(BaseSettings):
    used: Databases = Databases.PostgreSQL
    ip: str = "localhost"
    port: int = 5432
    user: str
    password: str
    name: str

    test_name: str | None = None
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: float = 30
    pool_recycle: int = 1800

    model_config = SettingsConfigDict(env_prefix="DB_")

    def build_postgres_url(
        self,
        database: str | None = None,
    ) -> str:
        return URL.create(
            drivername=f"postgresql+{PostgreSQLDrivers.ASYNC_DRIVER}",
            username=self.user,
            password=self.password,
            host=self.ip,
            port=self.port,
            database=database or self.name,
        ).render_as_string(hide_password=False)

    def build_mysql_url(
        self,
        database: str | None = None,
    ) -> str:
        return URL.create(
            drivername=f"mysql+{MySQLDrivers.ASYNC_DRIVER}",
            username=self.user,
            password=self.password,
            host=self.ip,
            port=self.port,
            database=database or self.name,
        ).render_as_string(hide_password=False)


class RedisSettings(BaseSettings):
    use: bool = False
    ip: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str | None = None
    socket_timeout: float = 5
    socket_connect_timeout: float = 5

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    def get_redis(self, db: int | None = None) -> Redis:
        return Redis(
            host=self.ip,
            port=self.port,
            password=self.password,
            db=self.db if db is None else db,
            socket_timeout=self.socket_timeout,
            socket_connect_timeout=self.socket_connect_timeout,
        )


class HealthcheckSettings(BaseSettings):
    timeout_seconds: float = 3

    model_config = SettingsConfigDict(env_prefix="HEALTHCHECK_")


class Settings(BaseSettings):
    log_chat: int | None = None
    admins: list[int] = Field(default_factory=list)
    debug_mode: bool = False

    app: AppSettings = Field(default_factory=AppSettings)
    bot: BotSettings = Field(default_factory=BotSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    healthcheck: HealthcheckSettings = Field(default_factory=HealthcheckSettings)


settings = Settings()
