import bot.middlewares as middlewares


def test_setup_middlewares_uses_configured_rate_limit(monkeypatch) -> None:
    captured: dict[str, float] = {}

    def setup_throttling_middleware(dp, rate_limit: float = 1.5) -> None:
        captured["rate_limit"] = rate_limit

    monkeypatch.setattr(middlewares.settings.bot, "rate_limit", 0.25)
    monkeypatch.setattr(middlewares, "setup_throttling_middleware", setup_throttling_middleware)
    monkeypatch.setattr(middlewares, "setup_get_repo_middleware", lambda dp: None)
    monkeypatch.setattr(middlewares, "setup_get_user_middleware", lambda dp: None)
    monkeypatch.setattr(middlewares, "setup_get_chat_middleware", lambda dp: None)

    middlewares.setup_middlewares(object())

    assert captured["rate_limit"] == 0.25
