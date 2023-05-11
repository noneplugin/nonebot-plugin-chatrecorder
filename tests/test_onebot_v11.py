from datetime import datetime
from typing import Literal, Optional

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
    from nonebot_plugin_chatrecorder.adapters.onebot_v11 import record_recv_msg

    async with app.test_api() as ctx:
        bot = ctx.create_bot(base=Bot, adapter=Adapter(get_driver()))
    assert isinstance(bot, Bot)

    time = 1000000
    user_id = 123456
    group_id = 654321
    message_id = 11451411111
    message = Message("test group message")
    event = fake_group_message_event(
        time=time,
        user_id=user_id,
        group_id=group_id,
        message_id=message_id,
        message=message,
    )
    await record_recv_msg(bot, event)
    await check_record(
        bot,
        str(message_id),
        "message",
        "group",
        message,
        str(user_id),
        str(group_id),
        time,
    )

    message_id = 11451422222
    message = Message("test private message")
    event = fake_private_message_event(
        time=time, user_id=user_id, message_id=message_id, message=message
    )
    await record_recv_msg(bot, event)
    await check_record(
        bot, str(message_id), "message", "private", message, str(user_id), None, time
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_chatrecorder.adapters.onebot_v11 import record_send_msg

    async with app.test_api() as ctx:
        bot = ctx.create_bot(base=Bot, adapter=Adapter(get_driver()))
    assert isinstance(bot, Bot)

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
        bot, str(message_id), "message_sent", "group", message, user_id=bot.self_id
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
        bot, str(message_id), "message_sent", "group", message, user_id=bot.self_id
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
        bot,
        str(message_id),
        "message_sent",
        "private",
        message,
        user_id=bot.self_id,
        group_id=None,
    )


async def check_record(
    bot: Bot,
    message_id: str,
    type: str,
    detail_type: str,
    message: "Message",
    user_id: str,
    group_id: Optional[str] = None,
    time: Optional[int] = None,
):
    from nonebot_plugin_datastore import create_session
    from sqlalchemy import select

    from nonebot_plugin_chatrecorder.adapters import serialize_message
    from nonebot_plugin_chatrecorder.model import MessageRecord

    statement = select(MessageRecord).where(MessageRecord.message_id == message_id)
    async with create_session() as session:
        records = (await session.scalars(statement)).all()

    assert len(records) == 1
    record = records[0]
    assert record.platform == "qq"
    assert record.type == type
    assert record.detail_type == detail_type
    assert record.message == serialize_message(bot, message)
    assert record.plain_text == message.extract_plain_text()
    assert record.user_id == user_id
    if group_id:
        assert record.group_id == group_id
    if time:
        assert record.time == datetime.utcfromtimestamp(time)
