from pathlib import Path

import nonebot
import pytest
from nonebot.adapters.console import Adapter as ConsoleAdapter
from nonebot.adapters.feishu import Adapter as FeishuAdapter
from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter
from nonebot.adapters.onebot.v12 import Adapter as OnebotV12Adapter
from nonebot.adapters.qqguild import Adapter as QQGuildAdapter
from nonebot.adapters.telegram import Adapter as TelegramAdapter
from nonebug import NONEBOT_INIT_KWARGS, App
from sqlalchemy import delete
from sqlalchemy.pool import StaticPool


def pytest_configure(config: pytest.Config) -> None:
    config.stash[NONEBOT_INIT_KWARGS] = {
        "datastore_database_url": "sqlite+aiosqlite://",
        "datastore_engine_options": {
            # https://github.com/miguelgrinberg/Flask-Migrate/issues/153#issuecomment-354711968
            # 必须保持连接，不然连接关闭后，内存中的数据库会被删除
            "poolclass": StaticPool,
        },
        "driver": "~fastapi+~websockets",
    }


@pytest.fixture
async def app(tmp_path: Path):
    nonebot.require("nonebot_plugin_chatrecorder")
    from nonebot_plugin_datastore.config import plugin_config
    from nonebot_plugin_datastore.db import create_session, init_db
    from nonebot_plugin_session.model import SessionModel

    from nonebot_plugin_chatrecorder.model import MessageRecord

    plugin_config.datastore_cache_dir = tmp_path / "cache"
    plugin_config.datastore_config_dir = tmp_path / "config"
    plugin_config.datastore_data_dir = tmp_path / "data"

    await init_db()

    yield App()

    async with create_session() as session, session.begin():
        await session.execute(delete(MessageRecord))
        await session.execute(delete(SessionModel))


@pytest.fixture(scope="session", autouse=True)
def load_adapters(nonebug_init: None):
    driver = nonebot.get_driver()
    driver.register_adapter(ConsoleAdapter)
    driver.register_adapter(OnebotV11Adapter)
    driver.register_adapter(OnebotV12Adapter)
    driver.register_adapter(QQGuildAdapter)
    driver.register_adapter(TelegramAdapter)
    driver.register_adapter(FeishuAdapter)
