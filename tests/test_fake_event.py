from datetime import datetime, timezone
from typing import Literal

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message, PrivateMessageEvent
from nonebot.adapters.onebot.v11.event import Sender
from nonebug.app import App
from pydantic import create_model

from .utils import check_record


def fake_private_message_event(**field) -> PrivateMessageEvent:
    _Fake = create_model("_Fake", __base__=PrivateMessageEvent)

    class FakeEvent(_Fake):
        time: int = 1000000
        self_id: int = 11
        post_type: Literal["message"] = "message"
        sub_type: str = "friend"
        user_id: int = 10
        message_type: Literal["private"] = "private"
        message_id: int = 1
        message: Message = Message("test")
        original_message: Message = Message("test")
        raw_message: str = "test"
        font: int = 0
        sender: Sender = Sender(nickname="test")
        to_me: bool = False

        class Config:
            extra = "forbid"

        def _is_fake(self) -> bool:
            return True

    return FakeEvent(**field)


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_chatrecorder.adapters.onebot_v11 import record_recv_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(base=Bot, adapter=Adapter(get_driver()), self_id="11")
    assert isinstance(bot, Bot)

    time = 1000000
    user_id = 123456

    message_id = 1145141919810
    message = Message("test private message")
    event = fake_private_message_event(
        time=time, user_id=user_id, message_id=message_id, message=message
    )
    await record_recv_msg(bot, event)
    await check_record(
        "11",
        "OneBot V11",
        "qq",
        1,
        str(user_id),
        None,
        None,
        datetime.fromtimestamp(time, timezone.utc),
        "fake",
        str(message_id),
        serialize_message(bot, message),
        message.extract_plain_text(),
    )