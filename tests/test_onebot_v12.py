from datetime import datetime
from typing import Literal, Optional

from nonebot.adapters.onebot.v12 import (
    Bot,
    ChannelMessageEvent,
    GroupMessageEvent,
    Message,
    PrivateMessageEvent,
)
from nonebot.adapters.onebot.v12.event import BotSelf
from nonebug.app import App
from pydantic import create_model


def fake_group_message_event(**field) -> GroupMessageEvent:
    _Fake = create_model("_Fake", __base__=GroupMessageEvent)

    class FakeEvent(_Fake):
        self: BotSelf = BotSelf(platform="qq", user_id="1")
        id: str = "12"
        time: datetime = datetime.fromtimestamp(1000000)
        type: Literal["message"] = "message"
        detail_type: Literal["group"] = "group"
        sub_type: str = ""
        message_id: str = "10"
        message: Message = Message("test")
        original_message: Message = Message("test")
        alt_message: str = "test"
        user_id: str = "100"
        group_id: str = "10000"
        to_me: bool = False

        class Config:
            extra = "forbid"

    return FakeEvent(**field)


def fake_private_message_event(**field) -> PrivateMessageEvent:
    _Fake = create_model("_Fake", __base__=PrivateMessageEvent)

    class FakeEvent(_Fake):
        self: BotSelf = BotSelf(platform="qq", user_id="1")
        id: str = "12"
        time: datetime = datetime.fromtimestamp(1000000)
        type: Literal["message"] = "message"
        detail_type: Literal["private"] = "private"
        sub_type: str = ""
        message_id: str = "10"
        message: Message = Message("test")
        original_message: Message = Message("test")
        alt_message: str = "test"
        user_id: str = "100"
        to_me: bool = False

        class Config:
            extra = "forbid"

    return FakeEvent(**field)


def fake_channel_message_event_v12(**field) -> ChannelMessageEvent:
    _Fake = create_model("_Fake", __base__=ChannelMessageEvent)

    class FakeEvent(_Fake):
        self: BotSelf = BotSelf(platform="qq", user_id="1")
        id: str = "12"
        time: datetime = datetime.fromtimestamp(1000000)
        type: Literal["message"] = "message"
        detail_type: Literal["channel"] = "channel"
        sub_type: str = ""
        message_id: str = "10"
        message: Message = Message("test")
        original_message: Message = Message("test")
        alt_message: str = "test"
        user_id: str = "100"
        guild_id: str = "10000"
        channel_id: str = "100000"
        to_me: bool = False

        class Config:
            extra = "forbid"

    return FakeEvent(**field)


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_chatrecorder.adapters.onebot_v12 import record_recv_msg

    async with app.test_api() as ctx:
        bot = ctx.create_bot(base=Bot, platform="qq")
    assert isinstance(bot, Bot)

    time = datetime.utcfromtimestamp(1000000)
    user_id = "111111"
    group_id = "222222"
    guild_id = "333333"
    channel_id = "444444"

    message_id = "11451411111"
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
        time,
        message_id,
        "group",
        message,
        bot.platform,
        user_id=user_id,
        group_id=group_id,
    )

    message_id = "11451422222"
    message = Message("test private message")
    event = fake_private_message_event(
        time=time, user_id=user_id, message_id=message_id, message=message
    )
    await record_recv_msg(bot, event)
    await check_record(
        time,
        message_id,
        "private",
        message,
        bot.platform,
        user_id=user_id,
    )

    message_id = "11451433333"
    message = Message("test channel message")
    event = fake_channel_message_event_v12(
        time=time,
        user_id=user_id,
        guild_id=guild_id,
        channel_id=channel_id,
        message_id=message_id,
        message=message,
    )
    await record_recv_msg(bot, event)
    await check_record(
        time,
        message_id,
        "channel",
        message,
        bot.platform,
        user_id=user_id,
        guild_id=guild_id,
        channel_id=channel_id,
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_chatrecorder.adapters.onebot_v12 import record_send_msg

    async with app.test_api() as ctx:
        bot = ctx.create_bot(base=Bot, platform="qq")
    assert isinstance(bot, Bot)

    time = 1000000
    user_id = "111111"
    group_id = "222222"
    guild_id = "333333"
    channel_id = "444444"

    message_id = "11451444444"
    message = Message("test call_api send_message group message")
    await record_send_msg(
        bot,
        None,
        "send_message",
        {
            "detail_type": "group",
            "group_id": group_id,
            "message": message,
        },
        {"message_id": message_id, "time": time},
    )
    await check_record(
        datetime.utcfromtimestamp(time),
        message_id,
        "group",
        message,
        bot.platform,
        send_msg=True,
        user_id=bot.self_id,
        group_id=group_id,
    )

    message_id = "11451455555"
    message = Message("test call_api send_message private message")
    await record_send_msg(
        bot,
        None,
        "send_message",
        {
            "detail_type": "private",
            "message": message,
        },
        {"message_id": message_id, "time": time},
    )
    await check_record(
        datetime.utcfromtimestamp(time),
        message_id,
        "private",
        message,
        bot.platform,
        send_msg=True,
        user_id=bot.self_id,
    )

    message_id = "11451466666"
    message = Message("test call_api send_message channel message")
    await record_send_msg(
        bot,
        None,
        "send_message",
        {
            "detail_type": "channel",
            "guild_id": guild_id,
            "channel_id": channel_id,
            "message": message,
        },
        {"message_id": message_id, "time": time},
    )
    await check_record(
        datetime.utcfromtimestamp(time),
        message_id,
        "channel",
        message,
        bot.platform,
        send_msg=True,
        user_id=bot.self_id,
        guild_id=guild_id,
        channel_id=channel_id,
    )


async def check_record(
    time: datetime,
    message_id: str,
    detail_type: str,
    message: "Message",
    platform: str,
    send_msg: bool = False,
    user_id: str = "",
    group_id: Optional[str] = None,
    guild_id: Optional[str] = None,
    channel_id: Optional[str] = None,
):
    from nonebot_plugin_datastore import create_session
    from sqlalchemy import select

    from nonebot_plugin_chatrecorder import serialize_message
    from nonebot_plugin_chatrecorder.model import MessageRecord

    statement = select(MessageRecord).where(MessageRecord.message_id == message_id)
    async with create_session() as session:
        records = (await session.scalars(statement)).all()

    assert len(records) == 1
    record = records[0]
    if send_msg:
        assert record.type == "message_sent"
    else:
        assert record.type == "message"
    assert record.detail_type == detail_type
    assert record.time == time
    assert record.platform == platform
    assert record.message == serialize_message(message)
    assert record.plain_text == message.extract_plain_text()
    assert record.user_id == user_id
    assert record.group_id == group_id
    assert record.guild_id == guild_id
    assert record.channel_id == channel_id
