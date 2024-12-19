from datetime import datetime, timezone
from typing import Literal

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import (
    Adapter,
    Bot,
    GroupMessageEvent,
    Message,
    PrivateMessageEvent,
)
from nonebot.adapters.onebot.v11.event import Sender
from nonebug.app import App
from pydantic import create_model

from .utils import check_record


def fake_group_message_event(**field) -> GroupMessageEvent:
    _Fake = create_model("_Fake", __base__=GroupMessageEvent)

    class FakeEvent(_Fake):
        time: int = 1000000
        self_id: int = 11
        post_type: Literal["message"] = "message"
        sub_type: str = "normal"
        user_id: int = 10
        message_type: Literal["group"] = "group"
        group_id: int = 10000
        message_id: int = 1
        message: Message = Message("test")
        original_message: Message = Message("test")
        raw_message: str = "test"
        font: int = 0
        sender: Sender = Sender(
            card="",
            nickname="test",
            role="member",
        )
        to_me: bool = False

        class Config:
            extra = "forbid"

    return FakeEvent(**field)


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

    return FakeEvent(**field)


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_uninfo import Scene, SceneType, Session, User

    from nonebot_plugin_chatrecorder.adapters.onebot_v11 import record_recv_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    time = 1000000
    user_id = 123456
    group_id = 654321
    group_msg = Message("test group message")
    group_msg_id = 11451411111

    private_msg = Message("test private message")
    private_msg_id = 11451422222

    async with app.test_api() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(base=Bot, adapter=adapter, self_id="11")

    event = fake_group_message_event(
        time=time,
        user_id=user_id,
        group_id=group_id,
        message_id=group_msg_id,
        message=group_msg,
    )
    session = Session(
        self_id="11",
        adapter="OneBot V11",
        scope="QQClient",
        scene=Scene(id=str(group_id), type=SceneType.GROUP),
        user=User(id=str(user_id)),
    )
    await record_recv_msg(event, session)
    await check_record(
        session,
        datetime.fromtimestamp(time, timezone.utc),
        "message",
        str(group_msg_id),
        serialize_message(bot, group_msg),
        group_msg.extract_plain_text(),
    )

    event = fake_private_message_event(
        time=time, user_id=user_id, message_id=private_msg_id, message=private_msg
    )
    session = Session(
        self_id="11",
        adapter="OneBot V11",
        scope="QQClient",
        scene=Scene(id=str(user_id), type=SceneType.PRIVATE),
        user=User(id=str(user_id)),
    )
    await record_recv_msg(event, session)
    await check_record(
        session,
        datetime.fromtimestamp(time, timezone.utc),
        "message",
        str(private_msg_id),
        serialize_message(bot, private_msg),
        private_msg.extract_plain_text(),
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_uninfo import Scene, SceneType, Session, User

    from nonebot_plugin_chatrecorder.adapters.onebot_v11 import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(base=Bot, adapter=adapter, self_id="11")

    user_id = 123456
    group_id = 654321

    message_id = 11451433333
    message = Message("test call_api send_msg")
    await record_send_msg(
        bot,
        None,
        "send_msg",
        {"message_type": "group", "group_id": group_id, "message": message},
        {"message_id": message_id},
    )
    await check_record(
        Session(
            self_id="11",
            adapter="OneBot V11",
            scope="QQClient",
            scene=Scene(id=str(group_id), type=SceneType.GROUP),
            user=User(id="11"),
        ),
        None,
        "message_sent",
        str(message_id),
        serialize_message(bot, message),
        message.extract_plain_text(),
    )

    message_id = 11451444444
    message = Message("test call_api send_group_msg")
    await record_send_msg(
        bot,
        None,
        "send_group_msg",
        {"group_id": group_id, "message": message},
        {"message_id": message_id},
    )
    await check_record(
        Session(
            self_id="11",
            adapter="OneBot V11",
            scope="QQClient",
            scene=Scene(id=str(group_id), type=SceneType.GROUP),
            user=User(id="11"),
        ),
        None,
        "message_sent",
        str(message_id),
        serialize_message(bot, message),
        message.extract_plain_text(),
    )

    message_id = 11451455555
    message = Message("test call_api send_private_msg")
    await record_send_msg(
        bot,
        None,
        "send_private_msg",
        {"user_id": user_id, "message": message},
        {"message_id": message_id},
    )
    await check_record(
        Session(
            self_id="11",
            adapter="OneBot V11",
            scope="QQClient",
            scene=Scene(id=str(user_id), type=SceneType.PRIVATE),
            user=User(id="11"),
        ),
        None,
        "message_sent",
        str(message_id),
        serialize_message(bot, message),
        message.extract_plain_text(),
    )
