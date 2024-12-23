import nonebot
import pytest
from nonebot.adapters.console import Adapter as ConsoleAdapter
from nonebot.adapters.discord import Adapter as DiscordAdapter
from nonebot.adapters.dodo import Adapter as DoDoAdapter
from nonebot.adapters.feishu import Adapter as FeishuAdapter
from nonebot.adapters.kaiheila import Adapter as KaiheilaAdapter
from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter
from nonebot.adapters.onebot.v12 import Adapter as OnebotV12Adapter
from nonebot.adapters.qq import Adapter as QQAdapter
from nonebot.adapters.satori import Adapter as SatoriAdapter
from nonebot.adapters.telegram import Adapter as TelegramAdapter
from nonebug import NONEBOT_INIT_KWARGS, App
from sqlalchemy import StaticPool, delete


def pytest_configure(config: pytest.Config) -> None:
    config.stash[NONEBOT_INIT_KWARGS] = {
        "sqlalchemy_database_url": "sqlite+aiosqlite:///:memory:",
        "sqlalchemy_engine_options": {"poolclass": StaticPool},
        "alembic_startup_check": False,
        "driver": "~fastapi+~websockets+~httpx",
    }


@pytest.fixture
async def app():
    nonebot.require("nonebot_plugin_chatrecorder")

    from nonebot_plugin_orm import get_session, init_orm
    from nonebot_plugin_uninfo.orm import BotModel, SceneModel, SessionModel, UserModel

    from nonebot_plugin_chatrecorder.model import MessageRecord

    await init_orm()

    yield App()

    async with get_session() as db_session:
        await db_session.execute(delete(MessageRecord))
        await db_session.execute(delete(SessionModel))
        await db_session.execute(delete(UserModel))
        await db_session.execute(delete(SceneModel))
        await db_session.execute(delete(BotModel))
        await db_session.commit()


@pytest.fixture(scope="session", autouse=True)
def after_nonebot_init(after_nonebot_init: None):
    driver = nonebot.get_driver()
    driver.register_adapter(ConsoleAdapter)
    driver.register_adapter(DiscordAdapter)
    driver.register_adapter(DoDoAdapter)
    driver.register_adapter(FeishuAdapter)
    driver.register_adapter(KaiheilaAdapter)
    driver.register_adapter(OnebotV11Adapter)
    driver.register_adapter(OnebotV12Adapter)
    driver.register_adapter(QQAdapter)
    driver.register_adapter(SatoriAdapter)
    driver.register_adapter(TelegramAdapter)
