from nonebot import require
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_session_orm")
require("nonebot_plugin_localstore")

from . import adapters as adapters
from .message import deserialize_message as deserialize_message
from .message import serialize_message as serialize_message
from .model import MessageRecord as MessageRecord
from .record import get_message_records as get_message_records
from .record import get_messages as get_messages
from .record import get_messages_plain_text as get_messages_plain_text

__plugin_meta__ = PluginMetadata(
    name="聊天记录",
    description="记录机器人收到和发出的消息",
    usage="请参考文档",
    type="library",
    homepage="https://github.com/noneplugin/nonebot-plugin-chatrecorder",
    supported_adapters={
        "~onebot.v11",
        "~onebot.v12",
        "~console",
        "~kaiheila",
        "~telegram",
        "~feishu",
        "~red",
        "~discord",
        "~dodo",
        "~satori",
        "~qq",
    },
)
