# Шаблон бота на Aiogram

Готовый к production шаблон для Telegram-ботов на aiogram 3, PostgreSQL, Redis и опциональном FastAPI-приложении для проверок доступности и готовности.

## Возможности

- Точка входа aiogram 3 в режиме long polling с роутерами, middleware, фильтрами и клавиатурами.
- Асинхронные репозитории SQLAlchemy 2, миграции Alembic и подключенный PostgreSQL-драйвер.
- Опциональное Redis-хранилище для FSM и ограничения частоты запросов.
- FastAPI-маршруты `/health/live` и `/health/ready` с параллельными dependency checks и таймаутами.
- Настраиваемые SQLAlchemy pool limits, Redis socket timeouts и `allowed_updates` для aiogram polling.
- Docker Compose стек с ботом, PostgreSQL, Redis, опциональным API-сервисом и one-shot migrator.
- Ruff, mypy, pytest, pre-commit и workflow для GitHub Actions.
- Тестовые значения по умолчанию позволяют запускать модульные тесты без локального `.env`; интеграционные тесты пропускаются, если PostgreSQL недоступен.

## Требования

- Python 3.11+
- Poetry 1.8+
- Docker и Docker Compose v2 для разработки в контейнерах

## Быстрый старт

```bash
cp .env.example .env
make install-dev
```

Отредактируйте `.env` и задайте минимум:

```dotenv
BOT_TOKEN=123456:telegram-token-from-BotFather
ADMINS=[123456789]
DB_USER=telegram_bot
DB_PASSWORD=telegram_bot
DB_NAME=telegram_bot
```

Запустите инфраструктуру:

```bash
docker compose up -d postgres redis
make migrate
make start
```

Запустите FastAPI-приложение для health-проверок локально:

```bash
make api
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

## Docker

Запустить полный стек:

```bash
make docker-up
```

Запустить также опциональный FastAPI-сервис:

```bash
docker compose --profile api up -d --build
```

Применить миграции внутри Docker Compose:

```bash
make docker-migrate
```

Полезные команды:

```bash
make docker-logs
make docker-down
```

## Команды разработки

```bash
make format      # форматирование и автоматические исправления
make lint        # ruff + mypy
make test        # тесты; DB-тесты пропускаются без PostgreSQL
make test-cov    # тесты с покрытием
make check       # статический анализ + тесты
```

Создать и применить миграции:

```bash
make migration message="add orders"
make migrate
```

В шаблоне уже есть initial Alembic revision для базовых таблиц `users` и `chats`.
Новые файлы в `migrations/versions/` считаются исходным кодом и должны попадать в git.
Тесты проверяют линейность Alembic history и прогон `upgrade head`/`downgrade base`
на тестовой PostgreSQL базе, когда она доступна.

## Документация

- [Архитектура](docs/architecture.md)
- [Production-чеклист](docs/production-checklist.md)

## Структура проекта

```text
bot/
  __main__.py              # точка входа long polling
  api.py                   # FastAPI-приложение для проверок доступности и готовности
  config.py                # bot, dispatcher, FSM-хранилище
  settings.py              # конфигурация pydantic-settings
  database/                # движок SQLAlchemy, модели, репозитории
  handlers/                # роутеры aiogram
  middlewares/             # DB/session, throttling и пример middleware
  filters/                 # фильтры aiogram
  keyboards/               # reply и inline-клавиатуры
migrations/                # окружение Alembic и ревизии
tests/
  unit/
  integration/
docs/
  architecture.md
  production-checklist.md
```

## Конфигурация

Конфигурация загружается из переменных окружения и `.env`.

Важные переменные:

- `BOT_TOKEN` - токен Telegram-бота от `@BotFather`.
- `ADMINS` - список Telegram user IDs в JSON-like формате, например `[111, 222]`.
- `DB_USED` - по умолчанию `PostgreSQL`. MySQL остаётся поддержанным в коде, но требует добавления `asyncmy`.
- `DB_IP`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` - настройки подключения к базе данных.
- `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE` - параметры пула SQLAlchemy.
- `REDIS_USE` - установите `True`, чтобы использовать FSM-хранилище на Redis.
- `REDIS_DB`, `REDIS_SOCKET_TIMEOUT`, `REDIS_SOCKET_CONNECT_TIMEOUT` - параметры Redis connection pool.
- `HEALTHCHECK_TIMEOUT_SECONDS` - максимальное время одной dependency check в `/health/ready`.
- `ALLOWED_UPDATES` - опциональный JSON-список update types для polling.
  Если не задан, aiogram вычисляет список по зарегистрированным routers.
- `APP_TIMEZONE` - timezone для сообщений логов при запуске и остановке.

## Заметки по тестам

Модульные тесты используют безопасные значения по умолчанию из `pyproject.toml`.

Интеграционные тесты создают и удаляют таблицы в настроенной PostgreSQL базе. Если PostgreSQL недоступен, локально они пропускаются. В GitHub Actions PostgreSQL запускается как сервис, и эти же тесты выполняются штатно.

## Чеклист для использования шаблона

Когда начинаете реальный проект на основе этого шаблона:

1. Обновите `README.md`, `.env.example`, `LICENSE` и ссылки на репозиторий.
2. Замените примерные handlers/keyboards на сценарии вашего бота.
3. Добавьте доменные модели, репозитории, сервисы и Alembic revisions.
4. Держите UX handlers, callback data и tests синхронизированными.
5. Включите Redis в `.env`, если FSM state должен переживать перезапуск процесса.
