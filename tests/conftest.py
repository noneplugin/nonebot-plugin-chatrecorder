from pathlib import Path

import nonebot
import pytest
from nonebug.app import App
from sqlalchemy import delete


@pytest.fixture(
    params=[
        {
            "datastore_database_url": "sqlite+aiosqlite:///:memory:",
        },
        {
            "datastore_database_url": "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        },
        {
            "datastore_database_url": "mysql+aiomysql:://mysql:mysql@localhost:3306/mysql",
        },
    ]
)
async def app(tmp_path: Path, request):

    nonebot.require("nonebot_plugin_chatrecorder")
    from nonebot_plugin_datastore.config import plugin_config
    from nonebot_plugin_datastore.db import create_session, init_db

    from nonebot_plugin_chatrecorder.model import MessageRecord

    plugin_config.datastore_cache_dir = tmp_path / "cache"
    plugin_config.datastore_config_dir = tmp_path / "config"
    plugin_config.datastore_data_dir = tmp_path / "data"

    if param := getattr(request, "param", {}):
        if database_url := param.get("datastore_database_url", ""):
            plugin_config.datastore_database_url = database_url

    await init_db()

    yield App()

    async with create_session() as session, session.begin():
        await session.execute(delete(MessageRecord))
