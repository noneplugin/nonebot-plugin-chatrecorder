from datetime import datetime

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


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_chatrecorder.adapters.dodo import record_recv_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=Adapter(get_driver()),
            self_id="2233",
            bot_config=BotConfig(client_id="1234", token="xxxx"),
        )

    event = ChannelMessageEvent(
        event_id="abcdef",
        event_type=EventType.MESSAGE,
        timestamp=datetime.utcfromtimestamp(12345678),
        dodo_source_id="3344",
        channel_id="5566",
        island_source_id="7788",
        message_id="123456",
        message_type=MessageType.TEXT,
        message_body=TextMessage(content="test channel message"),
        personal=Personal(
            nick_name="user",
            avatar_url="https://static.imdodo.com/DoDoAvatar.png",
            sex=Sex.FEMALE,
        ),
        member=Member(nick_name="user", join_time=datetime.fromtimestamp(11111111)),
    )
    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "DoDo",
        "dodo",
        3,
        "3344",
        "5566",
        "7788",
        datetime.utcfromtimestamp(12345678),
        "message",
        "123456",
        serialize_message(bot, Message("test channel message")),
        "test channel message",
    )

    event = PersonalMessageEvent(
        event_id="abcdef",
        event_type=EventType.PERSONAL_MESSAGE,
        timestamp=datetime.utcfromtimestamp(12345678),
        dodo_source_id="3344",
        island_source_id="7788",
        message_id="123457",
        message_type=MessageType.TEXT,
        message_body=TextMessage(content="test personal message"),
        personal=Personal(
            nick_name="user",
            avatar_url="https://static.imdodo.com/DoDoAvatar.png",
            sex=Sex.FEMALE,
        ),
    )
    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "DoDo",
        "dodo",
        1,
        "3344",
        None,
        "7788",
        datetime.utcfromtimestamp(12345678),
        "message",
        "123457",
        serialize_message(bot, Message("test personal message")),
        "test personal message",
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_chatrecorder.adapters.dodo import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=Adapter(get_driver()),
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
