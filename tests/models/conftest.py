# pylint: disable=no-member
from pytest import fixture
from playthrough-bot.consts import Engines
from playthrough-bot.models import Session
from playthrough-bot.models.utils import get_engine, ModelBase


@fixture
def mock_config(monkeypatch):
    def _mock_config(attr: str, value: any):
        monkeypatch.setattr(f"playthrough-bot.models.utils.config.{attr}", value)

    return _mock_config


@fixture
def init_db(mock_config):
    mock_config("DATABASE_CONFIG", {"engine": Engines.Memory, "options": {}})
    engine = get_engine()
    ModelBase.metadata.create_all(bind=engine)
    Session.configure(bind=engine)
    yield
