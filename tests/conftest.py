import pytest
from pathlib import Path
from nonebug.app import App


@pytest.fixture
async def app(
    nonebug_init: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> App:
    import nonebot

    config = nonebot.get_driver().config
    # 插件数据目录
    config.datastore_cache_dir = tmp_path / "cache"
    config.datastore_config_dir = tmp_path / "config"
    config.datastore_data_dir = tmp_path / "data"
    config.chatrecorder_record_send_msg = True

    # 加载插件
    nonebot.load_plugin("nonebot_plugin_chatrecorder")

    from nonebot_plugin_datastore.db import init_db

    await init_db()

    return App(monkeypatch)
