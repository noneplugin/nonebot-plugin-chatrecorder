from datetime import datetime, timezone

from nonebot import get_driver
from nonebot.adapters.dodo import (
    Adapter,
    Bot,
    ChannelMessageEvent,
    EventType,
    Message,
    PersonalMessageEvent,
)
from nonebot.adapters.dodo.config import BotConfig
from nonebot.adapters.dodo.models import (
    Member,
    MessageReturn,
    MessageType,
    Personal,
    Sex,
    TextMessage,
)
from nonebug.app import App

from .utils import check_record


def fake_channel_message_event(content: str, message_id: str) -> ChannelMessageEvent:
    return ChannelMessageEvent(
        event_id="abcdef",
        event_type=EventType.MESSAGE,
        timestamp=datetime.fromtimestamp(12345678, timezone.utc),
        dodo_source_id="3344",
        channel_id="5566",
        island_source_id="7788",
        message_id=message_id,
        message_type=MessageType.TEXT,
        message_body=TextMessage(content=content),
        personal=Personal(
            nick_name="user",
            avatar_url="https://static.imdodo.com/DoDoAvatar.png",
            sex=Sex.FEMALE,
        ),
        member=Member(nick_name="user", join_time=datetime.now()),
    )


def fake_personal_message_event(content: str, message_id: str) -> PersonalMessageEvent:
    return PersonalMessageEvent(
        event_id="abcdef",
        event_type=EventType.PERSONAL_MESSAGE,
        timestamp=datetime.fromtimestamp(12345678, timezone.utc),
        dodo_source_id="3344",
        island_source_id="7788",
        message_id=message_id,
        message_type=MessageType.TEXT,
        message_body=TextMessage(content=content),
        personal=Personal(
            nick_name="user",
            avatar_url="https://static.imdodo.com/DoDoAvatar.png",
            sex=Sex.FEMALE,
        ),
    )


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_chatrecorder.adapters.dodo import record_recv_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot,
            adapter=adapter,
            self_id="2233",
            bot_config=BotConfig(client_id="1234", token="xxxx"),
        )

    content = "test channel message"
    message_id = "123456"
    event = fake_channel_message_event(content, message_id)
    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "DoDo",
        "dodo",
        3,
        "3344",
        "5566",
        "7788",
        datetime.fromtimestamp(12345678, timezone.utc),
        "message",
        message_id,
        serialize_message(bot, Message(content)),
        content,
    )

    content = "test personal message"
    message_id = "123457"
    event = fake_personal_message_event(content, message_id)
    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "DoDo",
        "dodo",
        1,
        "3344",
        None,
        "7788",
        datetime.fromtimestamp(12345678, timezone.utc),
        "message",
        message_id,
        serialize_message(bot, Message(content)),
        content,
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_chatrecorder.adapters.dodo import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot,
            adapter=adapter,
            self_id="2233",
            bot_config=BotConfig(client_id="1234", token="xxxx"),
        )

    await record_send_msg(
        bot,
        None,
        "set_channel_message_send",
        {
            "channel_id": "5566",
            "message_type": MessageType.TEXT,
            "message_body": TextMessage(content="test send channel message"),
            "referenced_message_id": None,
        },
        MessageReturn(message_id="123458"),
    )
    await check_record(
        "2233",
        "DoDo",
        "dodo",
        3,
        None,
        "5566",
        None,
        None,
        "message_sent",
        "123458",
        serialize_message(bot, Message("test send channel message")),
        "test send channel message",
    )

    await record_send_msg(
        bot,
        None,
        "set_personal_message_send",
        {
            "island_source_id": "7788",
            "dodo_source_id": "3344",
            "message_type": MessageType.TEXT,
            "message_body": TextMessage(content="test send personal message"),
        },
        MessageReturn(message_id="123459"),
    )
    await check_record(
        "2233",
        "DoDo",
        "dodo",
        1,
        "3344",
        None,
        "7788",
        None,
        "message_sent",
        "123459",
        serialize_message(bot, Message("test send personal message")),
        "test send personal message",
    )
