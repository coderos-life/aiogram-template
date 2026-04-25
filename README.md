# Шаблон бота на Aiogram

Готовый к production шаблон для Telegram-ботов на aiogram 3, PostgreSQL, Redis и опциональном FastAPI-приложении для проверок доступности и готовности.

## Возможности

- Точка входа aiogram 3 в режиме long polling с роутерами, middleware, фильтрами и клавиатурами.
- Асинхронные репозитории SQLAlchemy 2, миграции Alembic и подключенный PostgreSQL-драйвер.
- Опциональное Redis-хранилище для FSM и ограничения частоты запросов.
- FastAPI-маршруты `/health/live` и `/health/ready` для проверок контейнера и платформы деплоя.
- Docker Compose стек с ботом, PostgreSQL, Redis и опциональным профилем API-сервиса.
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
```

## Конфигурация

Конфигурация загружается из переменных окружения и `.env`.

Важные переменные:

- `BOT_TOKEN` - токен Telegram-бота от `@BotFather`.
- `ADMINS` - список Telegram user IDs в JSON-like формате, например `[111, 222]`.
- `DB_USED` - по умолчанию `PostgreSQL`. MySQL остаётся поддержанным в коде, но требует добавления `asyncmy`.
- `DB_IP`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` - настройки подключения к базе данных.
- `REDIS_USE` - установите `True`, чтобы использовать FSM-хранилище на Redis.
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
