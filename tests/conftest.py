from pathlib import Path

import pytest
from nonebug.app import App

from .utils import clear_plugins


@pytest.fixture
async def app(nonebug_init: None, tmp_path: Path, request):
    import nonebot

    config = nonebot.get_driver().config
    # 插件数据目录
    config.datastore_cache_dir = tmp_path / "cache"
    config.datastore_config_dir = tmp_path / "config"
    config.datastore_data_dir = tmp_path / "data"
    # 设置配置
    if param := getattr(request, "param", {}):
        for k, v in param.items():
            setattr(config, k, v)

    clear_plugins()

    # 加载插件
    nonebot.load_plugin("nonebot_plugin_chatrecorder")

    from nonebot_plugin_datastore.db import init_db

    await init_db()

    yield App()

    # 清除之前设置的配置
    delattr(config, "datastore_cache_dir")
    delattr(config, "datastore_config_dir")
    delattr(config, "datastore_data_dir")
    if param := getattr(request, "param", {}):
        for k in param.keys():
            delattr(config, k)
