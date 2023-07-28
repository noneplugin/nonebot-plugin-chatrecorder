from datetime import datetime
from typing import Literal, Optional

from nonebot import get_driver
from nonebot.adapters.onebot.v12 import (
    Adapter,
    Bot,
    ChannelMessageEvent,
    GroupMessageEvent,
    Message,
    PrivateMessageEvent,
)
from nonebot.adapters.onebot.v12.event import BotSelf
from nonebug.app import App
from pydantic import create_model

from .utils import check_record


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
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=Adapter(get_driver()),
            self_id="12",
            platform="qq",
            impl="walle-q",
        )
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
        "12",
        "OneBot V12",
        "qq",
        "LEVEL2",
        str(user_id),
        str(group_id),
        None,
        time,
        "message",
        str(message_id),
        serialize_message(bot, message),
        message.extract_plain_text(),
    )

    message_id = "11451422222"
    message = Message("test private message")
    event = fake_private_message_event(
        time=time, user_id=user_id, message_id=message_id, message=message
    )
    await record_recv_msg(bot, event)
    await check_record(
        "12",
        "OneBot V12",
        "qq",
        "LEVEL1",
        str(user_id),
        None,
        None,
        time,
        "message",
        str(message_id),
        serialize_message(bot, message),
        message.extract_plain_text(),
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
        "12",
        "OneBot V12",
        "qq",
        "LEVEL3",
        str(user_id),
        str(channel_id),
        str(guild_id),
        time,
        "message",
        str(message_id),
        serialize_message(bot, message),
        message.extract_plain_text(),
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_chatrecorder.adapters.onebot_v12 import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=Adapter(get_driver()),
            self_id="12",
            platform="qq",
            impl="walle-q",
        )
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
        "12",
        "OneBot V12",
        "qq",
        "LEVEL2",
        None,
        str(group_id),
        None,
        datetime.utcfromtimestamp(time),
        "message_sent",
        str(message_id),
        serialize_message(bot, message),
        message.extract_plain_text(),
    )

    message_id = "11451455555"
    message = Message("test call_api send_message private message")
    await record_send_msg(
        bot,
        None,
        "send_message",
        {
            "detail_type": "private",
            "user_id": user_id,
            "message": message,
        },
        {"message_id": message_id, "time": time},
    )
    await check_record(
        "12",
        "OneBot V12",
        "qq",
        "LEVEL1",
        str(user_id),
        None,
        None,
        datetime.utcfromtimestamp(time),
        "message_sent",
        str(message_id),
        serialize_message(bot, message),
        message.extract_plain_text(),
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
        "12",
        "OneBot V12",
        "qq",
        "LEVEL3",
        None,
        str(channel_id),
        str(guild_id),
        datetime.utcfromtimestamp(time),
        "message_sent",
        str(message_id),
        serialize_message(bot, message),
        message.extract_plain_text(),
    )
