from datetime import datetime

from nonebot import get_driver
from nonebot.adapters.telegram import Adapter, Bot, Message
from nonebot.adapters.telegram.config import BotConfig
from nonebot.adapters.telegram.event import (
    Event,
    ForumTopicMessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
)
from nonebot.adapters.telegram.model import InputMediaPhoto
from nonebug import App

from .utils import check_record


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_chatrecorder.adapters.telegram import record_recv_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=Adapter(get_driver()),
            self_id="2233",
            config=BotConfig(token="2233:xxx"),
        )
    assert isinstance(bot, Bot)

    event = Event.parse_event(
        {
            "update_id": 10000,
            "message": {
                "message_id": 1234,
                "date": 1122,
                "chat": {"id": 3344, "type": "private"},
                "from": {"id": 3344, "is_bot": False, "first_name": "test"},
                "text": "test private message",
            },
        }
    )
    assert isinstance(event, PrivateMessageEvent)

    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "Telegram",
        "telegram",
        1,
        "3344",
        None,
        None,
        datetime.utcfromtimestamp(1122),
        "message",
        "3344_1234",
        serialize_message(bot, Message("test private message")),
        "test private message",
    )

    event = Event.parse_event(
        {
            "update_id": 10000,
            "message": {
                "message_id": 1235,
                "date": 1122,
                "chat": {"id": 5566, "type": "group"},
                "from": {"id": 3344, "is_bot": False, "first_name": "test"},
                "text": "test group message",
            },
        }
    )
    assert isinstance(event, GroupMessageEvent)

    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "Telegram",
        "telegram",
        2,
        "3344",
        "5566",
        None,
        datetime.utcfromtimestamp(1122),
        "message",
        "5566_1235",
        serialize_message(bot, Message("test group message")),
        "test group message",
    )

    event = Event.parse_event(
        {
            "update_id": 10000,
            "message": {
                "message_id": 1236,
                "date": 1122,
                "chat": {"id": 5566, "type": "group"},
                "from": {"id": 3344, "first_name": "test", "is_bot": False},
                "message_thread_id": 6677,
                "is_topic_message": True,
                "text": "test forum topic message",
            },
        }
    )
    assert isinstance(event, ForumTopicMessageEvent)

    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "Telegram",
        "telegram",
        3,
        "3344",
        "6677",
        "5566",
        datetime.utcfromtimestamp(1122),
        "message",
        "5566_1236",
        serialize_message(bot, Message("test forum topic message")),
        "test forum topic message",
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_chatrecorder.adapters.telegram import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=Adapter(get_driver()),
            self_id="2233",
            config=BotConfig(token="2233:xxx"),
        )
    assert isinstance(bot, Bot)

    await record_send_msg(
        bot,
        None,
        "send_message",
        {
            "chat_id": 3344,
            "message_thread_id": None,
            "text": "test call_api send_message",
            "entities": None,
            "disable_notification": None,
            "protect_content": None,
            "reply_to_message_id": None,
            "allow_sending_without_reply": None,
            "parse_mode": None,
            "disable_web_page_preview": None,
            "reply_markup": None,
        },
        {
            "message_id": 1237,
            "from": {
                "id": 2233,
                "is_bot": True,
                "first_name": "bot",
                "username": "bot",
            },
            "chat": {
                "id": 3344,
                "first_name": "user",
                "username": "user",
                "type": "private",
            },
            "date": 1122,
            "text": "test call_api send_message",
        },
    )
    await check_record(
        "2233",
        "Telegram",
        "telegram",
        1,
        "3344",
        None,
        None,
        datetime.utcfromtimestamp(1122),
        "message_sent",
        "3344_1237",
        serialize_message(bot, Message("test call_api send_message")),
        "test call_api send_message",
    )

    await record_send_msg(
        bot,
        None,
        "send_media_group",
        {
            "chat_id": 3344,
            "message_thread_id": None,
            "media": [
                InputMediaPhoto(
                    type="photo",
                    media="attach://ac01.jpg",
                    caption=None,
                    parse_mode=None,
                    caption_entities=None,
                ),
                InputMediaPhoto(
                    type="photo",
                    media="attach://ac02.jpg",
                    caption=None,
                    parse_mode=None,
                    caption_entities=None,
                ),
            ],
            "disable_notification": None,
            "protect_content": None,
            "reply_to_message_id": None,
            "allow_sending_without_reply": None,
        },
        [
            {
                "message_id": 1238,
                "from": {
                    "id": 2233,
                    "is_bot": True,
                    "first_name": "bot",
                    "username": "bot",
                },
                "chat": {
                    "id": 3344,
                    "first_name": "user",
                    "username": "user",
                    "type": "private",
                },
                "date": 1122,
                "media_group_id": "114514",
                "photo": [
                    {
                        "file_id": "abcd",
                        "file_unique_id": "abcd",
                        "file_size": 1000,
                        "width": 100,
                        "height": 100,
                    }
                ],
            },
            {
                "message_id": 1239,
                "from": {
                    "id": 2233,
                    "is_bot": True,
                    "first_name": "bot",
                    "username": "bot",
                },
                "chat": {
                    "id": 3344,
                    "first_name": "user",
                    "username": "user",
                    "type": "private",
                },
                "date": 1122,
                "media_group_id": "114514",
                "photo": [
                    {
                        "file_id": "bcde",
                        "file_unique_id": "bcde",
                        "file_size": 1000,
                        "width": 100,
                        "height": 100,
                    }
                ],
            },
        ],
    )
    await check_record(
        "2233",
        "Telegram",
        "telegram",
        1,
        "3344",
        None,
        None,
        datetime.utcfromtimestamp(1122),
        "message_sent",
        "3344_1238_1239",
        [
            {"type": "photo", "data": {"file": "abcd"}},
            {"type": "photo", "data": {"file": "bcde"}},
        ],
        "",
    )
