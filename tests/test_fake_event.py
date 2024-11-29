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
    from nonebot_plugin_uninfo import Scene, SceneType, Session, User

    from nonebot_plugin_chatrecorder.message import serialize_message

    time = 1000000
    user_id = 123456
    message_id = 1145141919810
    message = Message("test private message")

    async with app.test_matcher() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(base=Bot, adapter=adapter, self_id="11")

        event = fake_private_message_event(
            time=time, user_id=user_id, message_id=message_id, message=message
        )
        ctx.receive_event(bot, event)

    await check_record(
        Session(
            self_id="11",
            adapter="OneBot V11",
            scope="QQClient",
            scene=Scene(id=str(user_id), type=SceneType.PRIVATE),
            user=User(id=str(user_id)),
        ),
        datetime.fromtimestamp(time, timezone.utc),
        "fake",
        str(message_id),
        serialize_message(bot, message),
        message.extract_plain_text(),
    )
