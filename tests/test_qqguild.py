from datetime import datetime, timedelta, timezone

from nonebot import get_driver
from nonebot.adapters.qqguild import Adapter, Bot, Message
from nonebot.adapters.qqguild.api import User
from nonebot.adapters.qqguild.api.model import Message as GuildMessage
from nonebot.adapters.qqguild.config import BotInfo
from nonebot.adapters.qqguild.event import (
    DirectMessageCreateEvent,
    EventType,
    MessageCreateEvent,
)
from nonebug import App

from .utils import check_record


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_chatrecorder.adapters.qqguild import record_recv_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=Adapter(get_driver()),
            self_id="2233",
            bot_info=BotInfo(id="2233", token="", secret=""),
        )

    event = MessageCreateEvent(
        __type__=EventType.CHANNEL_CREATE,
        id="1234",
        timestamp=datetime(
            2023, 7, 30, 8, 0, 0, 0, tzinfo=timezone(timedelta(hours=8))
        ),
        channel_id=6677,
        guild_id=5566,
        author=User(id=3344),
        content="test message create event",
    )
    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "QQ Guild",
        "qqguild",
        "LEVEL3",
        "3344",
        "6677",
        "5566",
        datetime(2023, 7, 30, 0, 0, 0, 0, tzinfo=timezone.utc),
        "message",
        "1234",
        serialize_message(bot, Message("test message create event")),
        "test message create event",
    )

    event = DirectMessageCreateEvent(
        __type__=EventType.DIRECT_MESSAGE_CREATE,
        id="1235",
        timestamp=datetime(
            2023, 7, 30, 8, 0, 0, 0, tzinfo=timezone(timedelta(hours=8))
        ),
        guild_id=5566,
        author=User(id=3344),
        content="test direct message create event",
    )
    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "QQ Guild",
        "qqguild",
        "LEVEL1",
        "3344",
        None,
        "5566",
        datetime(2023, 7, 30, 0, 0, 0, 0, tzinfo=timezone.utc),
        "message",
        "1235",
        serialize_message(bot, Message("test direct message create event")),
        "test direct message create event",
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""

    from nonebot_plugin_chatrecorder.adapters.qqguild import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=Adapter(get_driver()),
            self_id="2233",
            bot_info=BotInfo(id="2233", token="", secret=""),
        )

    await record_send_msg(
        bot,
        None,
        "post_messages",
        {
            "channel_id": 6677,
            "msg_id": "1236",
            "content": "test post_messages",
            "embed": None,
            "ark": None,
            "image": None,
            "file_image": None,
            "markdown": None,
            "message_reference": None,
        },
        GuildMessage(
            id="1236",
            channel_id=6677,
            guild_id=5566,
            content="test post_messages",
            timestamp=datetime(
                2023, 7, 30, 8, 0, 0, 0, tzinfo=timezone(timedelta(hours=8))
            ),
            author=User(id=333444),
        ),
    )
    await check_record(
        "2233",
        "QQ Guild",
        "qqguild",
        "LEVEL3",
        None,
        "6677",
        "5566",
        datetime(2023, 7, 30, 0, 0, 0, 0, tzinfo=timezone.utc),
        "message_sent",
        "1236",
        serialize_message(bot, Message("test post_messages")),
        "test post_messages",
    )

    await record_send_msg(
        bot,
        None,
        "post_dms_messages",
        {
            "guild_id": 5566,
            "msg_id": "1237",
            "content": "test post_dms_messages",
            "embed": None,
            "ark": None,
            "image": None,
            "file_image": None,
            "markdown": None,
            "message_reference": None,
        },
        GuildMessage(
            id="1237",
            guild_id=5566,
            content="test post_dms_messages",
            timestamp=datetime(
                2023, 7, 30, 8, 0, 0, 0, tzinfo=timezone(timedelta(hours=8))
            ),
            author=User(id=333444),
        ),
    )
    await check_record(
        "2233",
        "QQ Guild",
        "qqguild",
        "LEVEL1",
        None,
        None,
        "5566",
        datetime(2023, 7, 30, 0, 0, 0, 0, tzinfo=timezone.utc),
        "message_sent",
        "1237",
        serialize_message(bot, Message("test post_dms_messages")),
        "test post_dms_messages",
    )
