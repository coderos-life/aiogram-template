import asyncio

from fastapi.testclient import TestClient

import bot.api as api


def test_live_healthcheck() -> None:
    client = TestClient(api.create_app())

    response = client.get("/health/live")

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "ok"
    assert body["checks"] == {"app": "ok"}
    assert body["app"] == api.settings.app.name
    assert body["version"] == api.settings.app.version
    assert body["environment"] == api.settings.app.environment
    assert isinstance(body["uptime_seconds"], float)


def test_ready_healthcheck_returns_ok(monkeypatch) -> None:
    async def check_database() -> str:
        return "ok"

    async def check_redis() -> str:
        return "disabled"

    monkeypatch.setattr(api, "_check_database", check_database)
    monkeypatch.setattr(api, "_check_redis", check_redis)

    client = TestClient(api.create_app())

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["checks"] == {"database": "ok", "redis": "disabled"}


def test_ready_healthcheck_returns_degraded_on_failed_dependency(monkeypatch) -> None:
    async def check_database() -> str:
        return "error: OperationalError"

    async def check_redis() -> str:
        return "disabled"

    monkeypatch.setattr(api, "_check_database", check_database)
    monkeypatch.setattr(api, "_check_redis", check_redis)

    client = TestClient(api.create_app())

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    assert response.json()["checks"] == {"database": "error: OperationalError", "redis": "disabled"}


def test_ready_healthcheck_bounds_slow_dependency(monkeypatch) -> None:
    async def check_database() -> str:
        await asyncio.sleep(0.05)
        return "ok"

    async def check_redis() -> str:
        return "disabled"

    monkeypatch.setattr(api, "_check_database", check_database)
    monkeypatch.setattr(api, "_check_redis", check_redis)
    monkeypatch.setattr(api.settings.healthcheck, "timeout_seconds", 0.01)

    client = TestClient(api.create_app())

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    assert response.json()["checks"] == {"database": "error: TimeoutError", "redis": "disabled"}
