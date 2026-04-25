from fastapi.testclient import TestClient

from bot.api import create_app


def test_live_healthcheck() -> None:
    client = TestClient(create_app())

    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"app": "ok"}}
