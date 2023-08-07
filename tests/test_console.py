from datetime import datetime

from nonebot import get_driver
from nonebot.adapters.console import Adapter, Bot, Message, MessageEvent
from nonebug.app import App
from nonechat import ConsoleMessage, Text
from nonechat.info import User
from pydantic import create_model

from .utils import check_record


def fake_message_event(**field) -> MessageEvent:
    _Fake = create_model("_Fake", __base__=MessageEvent)

    class FakeEvent(_Fake):
        time: datetime = datetime.utcfromtimestamp(1000000)
        self_id: str = "console"
        post_type: str = "message"
        user: User = User(id="User")
        message: Message = Message("test")

        class Config:
            extra = "forbid"

    return FakeEvent(**field)


async def test_record_recv_msg(app: App):
    # 测试记录收到的消息
    from nonebot_plugin_chatrecorder.adapters.console import record_recv_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(base=Bot, adapter=Adapter(get_driver()), self_id="console")
    assert isinstance(bot, Bot)

    time = 1000000
    user_id = "User"
    message = Message("test_record_recv_msg")
    event = fake_message_event(
        time=datetime.fromtimestamp(time), user=User(id=user_id), message=message
    )
    await record_recv_msg(bot, event)
    await check_record(
        "console",
        "Console",
        "console",
        "LEVEL1",
        user_id,
        None,
        None,
        datetime.utcfromtimestamp(time),
        "message",
        "0",
        serialize_message(bot, message),
        message.extract_plain_text(),
    )


async def test_record_send_msg(app: App):
    # 测试记录发送的消息
    from nonebot_plugin_chatrecorder.adapters.console import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(base=Bot, adapter=Adapter(get_driver()), self_id="console")
    assert isinstance(bot, Bot)

    user_id = "User"
    elements = ConsoleMessage([Text("test_record_send_msg")])
    message = Message("test_record_send_msg")
    await record_send_msg(
        bot, None, "send_msg", {"user_id": user_id, "message": elements}, None
    )
    await check_record(
        "console",
        "Console",
        "console",
        "LEVEL1",
        user_id,
        None,
        None,
        None,
        "message_sent",
        "1",
        serialize_message(bot, message),
        message.extract_plain_text(),
    )
