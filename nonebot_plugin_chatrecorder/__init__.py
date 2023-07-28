from nonebot import require
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_session")
require("nonebot_plugin_datastore")

from nonebot_plugin_datastore.db import pre_db_init


@pre_db_init
async def _():
    from nonebot_plugin_datastore.script.command import upgrade
    from nonebot_plugin_datastore.script.utils import Config

    config = Config("nonebot_plugin_session")
    await upgrade(config, "head")

from . import adapters
from .message import deserialize_message, serialize_message
from .model import MessageRecord
from .record import get_message_records, get_messages, get_messages_plain_text

__plugin_meta__ = PluginMetadata(
    name="聊天记录",
    description="记录机器人收到和发出的消息",
    usage="请参考文档",
    type="library",
    homepage="https://github.com/noneplugin/nonebot-plugin-chatrecorder",
    supported_adapters={"~onebot.v11", "~onebot.v12"},
)
