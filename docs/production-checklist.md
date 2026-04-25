# Production-чеклист

## Перед первым запуском

- Замените `APP_NAME`, `APP_VERSION`, `BOT_TOKEN`, `ADMINS` и настройки БД в `.env`.
- Проверьте, что `.env` не попадает в git.
- Сгенерируйте и закоммитьте Alembic migration для новых моделей.
- Выполните `make check`.
- Выполните `make migrate` или `make docker-migrate`.

## Надёжность

- Включите Redis, если FSM state должен переживать рестарт процесса.
- Подберите `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT` под лимиты PostgreSQL и ожидаемую нагрузку.
- Оставьте `HEALTHCHECK_TIMEOUT_SECONDS` небольшим, чтобы readiness endpoint быстро снимал инстанс
  с трафика при деградации.
- Для webhook-режима добавьте отдельный entrypoint и TLS/reverse proxy конфигурацию.
  Текущий шаблон запускает long polling.

## Наблюдаемость

- Используйте `/health/live` для liveness probe.
- Используйте `/health/ready` для readiness probe.
- Настройте `LOG_CHAT`, если хотите получать error/info события в Telegram.
- Для продакшена подключите внешнюю систему логов на уровне платформы деплоя.

## Безопасность

- Не логируйте токены, пароли, платежные payloads и персональные данные без явной необходимости.
- Callback data должна быть компактной и валидируемой.
- Для платежей, заказов и прав доступа используйте fail-closed поведение.
- Для публичного репозитория включите GitHub security advisories и Dependabot alerts.
