from datetime import datetime, timezone

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
from nonebot_plugin_uninfo import Scene, SceneType, Session, User
from nonebug import App

from .utils import check_record


def fake_private_message_event(text: str, message_id: str) -> PrivateMessageEvent:
    event = Event.parse_event(
        {
            "update_id": 10000,
            "message": {
                "message_id": message_id,
                "date": 1122,
                "chat": {"id": 3344, "type": "private"},
                "from": {"id": 3344, "is_bot": False, "first_name": "test"},
                "text": text,
            },
        }
    )
    assert isinstance(event, PrivateMessageEvent)
    return event


def fake_group_message_event(text: str, message_id: str) -> GroupMessageEvent:
    event = Event.parse_event(
        {
            "update_id": 10000,
            "message": {
                "message_id": message_id,
                "date": 1122,
                "chat": {"id": 5566, "type": "group"},
                "from": {"id": 3344, "is_bot": False, "first_name": "test"},
                "text": text,
            },
        }
    )
    assert isinstance(event, GroupMessageEvent)
    return event


def fake_forum_topic_message_event(
    text: str, message_id: str
) -> ForumTopicMessageEvent:
    event = Event.parse_event(
        {
            "update_id": 10000,
            "message": {
                "message_id": message_id,
                "date": 1122,
                "chat": {"id": 5566, "type": "group"},
                "from": {"id": 3344, "is_bot": False, "first_name": "test"},
                "message_thread_id": 6677,
                "is_topic_message": True,
                "text": text,
            },
        }
    )
    assert isinstance(event, ForumTopicMessageEvent)
    return event


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_chatrecorder.message import serialize_message

    private_msg = "test private message"
    private_msg_id = "1234"

    group_msg = "test group message"
    group_msg_id = "1235"

    forum_msg = "test forum topic message"
    forum_msg_id = "1236"

    async with app.test_matcher() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot,
            adapter=adapter,
            self_id="2233",
            config=BotConfig(token="2233:xxx"),
        )

        event = fake_private_message_event(private_msg, private_msg_id)
        ctx.receive_event(bot, event)

        event = fake_group_message_event(group_msg, group_msg_id)
        ctx.receive_event(bot, event)

        event = fake_forum_topic_message_event(forum_msg, forum_msg_id)
        ctx.receive_event(bot, event)

    await check_record(
        Session(
            self_id="2233",
            adapter="Telegram",
            scope="Telegram",
            scene=Scene(id="3344", type=SceneType.PRIVATE),
            user=User(id="3344"),
        ),
        datetime.fromtimestamp(1122, timezone.utc),
        "message",
        "3344_1234",
        serialize_message(bot, Message(private_msg)),
        private_msg,
    )

    await check_record(
        Session(
            self_id="2233",
            adapter="Telegram",
            scope="Telegram",
            scene=Scene(id="5566", type=SceneType.GROUP),
            user=User(id="3344"),
        ),
        datetime.fromtimestamp(1122, timezone.utc),
        "message",
        "5566_1235",
        serialize_message(bot, Message(group_msg)),
        group_msg,
    )

    await check_record(
        Session(
            self_id="2233",
            adapter="Telegram",
            scope="Telegram",
            scene=Scene(
                id="6677",
                type=SceneType.CHANNEL_TEXT,
                parent=Scene(id="5566", type=SceneType.GUILD),
            ),
            user=User(id="3344"),
        ),
        datetime.fromtimestamp(1122, timezone.utc),
        "message",
        "5566_1236",
        serialize_message(bot, Message(forum_msg)),
        forum_msg,
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_chatrecorder.adapters.telegram import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot,
            adapter=adapter,
            self_id="2233",
            config=BotConfig(token="2233:xxx"),
        )

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
        Session(
            self_id="2233",
            adapter="Telegram",
            scope="Telegram",
            scene=Scene(id="3344", type=SceneType.PRIVATE),
            user=User(id="2233"),
        ),
        datetime.fromtimestamp(1122, timezone.utc),
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
        Session(
            self_id="2233",
            adapter="Telegram",
            scope="Telegram",
            scene=Scene(id="3344", type=SceneType.PRIVATE),
            user=User(id="2233"),
        ),
        datetime.fromtimestamp(1122, timezone.utc),
        "message_sent",
        "3344_1238_1239",
        [
            {"type": "photo", "data": {"file": "abcd"}},
            {"type": "photo", "data": {"file": "bcde"}},
        ],
        "",
    )
