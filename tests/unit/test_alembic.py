from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


PROJECT_DIR = Path(__file__).resolve().parents[2]


def make_alembic_config() -> Config:
    return Config(str(PROJECT_DIR / "alembic.ini"))


def test_alembic_has_single_linear_head() -> None:
    script = ScriptDirectory.from_config(make_alembic_config())

    assert script.get_heads() == ["001"]
    assert script.get_base() == "001"


def test_alembic_revisions_have_upgrade_and_downgrade() -> None:
    script = ScriptDirectory.from_config(make_alembic_config())
    revisions = list(script.walk_revisions())

    assert revisions
    for revision in revisions:
        module = revision.module
        assert callable(module.upgrade)
        assert callable(module.downgrade)
