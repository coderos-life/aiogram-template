# Архитектура шаблона

## Runtime-поток

```text
Telegram update
  -> aiogram Dispatcher
  -> middlewares: throttling, repo, user, chat
  -> routers/handlers
  -> services/repositories
  -> PostgreSQL / Redis
```

`bot/__main__.py` запускает long polling, проверяет Redis и PostgreSQL перед стартом,
регистрирует middleware и routers, а на shutdown закрывает SQLAlchemy engine.

## Конфигурация

Настройки находятся в `bot/settings.py` и читаются из переменных окружения или `.env`.

- `AppSettings` - имя, версия, окружение и timezone приложения.
- `BotSettings` - токен, parse mode, rate limit и опциональный список `allowed_updates`.
- `DatabaseSettings` - подключение к БД и параметры пула SQLAlchemy.
- `RedisSettings` - подключение Redis, номер DB и socket timeouts.
- `HealthcheckSettings` - таймаут dependency checks для FastAPI readiness endpoint.

## Health API

`bot/api.py` содержит отдельное FastAPI-приложение:

- `/health/live` возвращает состояние процесса.
- `/health/ready` параллельно проверяет PostgreSQL и Redis, ограничивает каждую проверку таймаутом
  и возвращает `503`, если зависимость недоступна.

API можно запускать отдельным контейнером через compose profile `api`.

## Database layer

`bot/database/repos` содержит репозитории поверх `AsyncSession`.
Доменные операции должны добавляться в конкретные repos, а не напрямую в handlers.
Миграции Alembic в `migrations/versions` являются исходным кодом проекта и должны коммититься.
Initial revision `001_initial_schema.py` создаёт базовые таблицы шаблона.

## Bot layer

Handlers должны оставаться тонкими:

1. Достать данные из update/FSM/repo.
2. Вызвать сервис или repository.
3. Вернуть пользователю сообщение/клавиатуру.

Callback data, keyboards и handlers нужно менять синхронно и покрывать тестами.
