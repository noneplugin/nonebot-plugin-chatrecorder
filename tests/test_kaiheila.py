import json
from datetime import datetime, timezone

from nonebot import get_driver
from nonebot.adapters.kaiheila import Adapter, Bot, Message, MessageSegment
from nonebot.adapters.kaiheila.api.model import MessageCreateReturn
from nonebot.adapters.kaiheila.event import (
    ChannelMessageEvent,
    EventMessage,
    Extra,
    PrivateMessageEvent,
    User,
)
from nonebot.compat import type_validate_python
from nonebug.app import App

from .utils import check_record


def fake_private_message_event(content: str, msg_id: str) -> PrivateMessageEvent:
    return type_validate_python(
        PrivateMessageEvent,
        {
            "post_type": "message",
            "channel_type": "PERSON",
            "type": 1,
            "target_id": "6677",
            "author_id": "3344",
            "content": content,
            "msg_id": msg_id,
            "msg_timestamp": 1234000,
            "nonce": "",
            "extra": Extra(type=1),  # type: ignore
            "user_id": "3344",
            "self_id": "2233",
            "message_type": "private",
            "sub_type": "",
            "event": EventMessage(
                type=1,
                content="test private message",  # type: ignore
                author=User(id="3344"),
                kmarkdown={
                    "raw_content": content,
                    "mention_part": [],
                    "mention_role_part": [],
                },  # type: ignore
            ),
        },
    )


def fake_channel_message_event(content: str, msg_id: str) -> ChannelMessageEvent:
    return type_validate_python(
        ChannelMessageEvent,
        {
            "post_type": "message",
            "channel_type": "GROUP",
            "type": 1,
            "target_id": "6677",
            "author_id": "3344",
            "content": content,
            "msg_id": msg_id,
            "msg_timestamp": 1234000,
            "nonce": "",
            "extra": Extra(
                type=1,
                guild_id="5566",
            ),  # type: ignore
            "user_id": "3344",
            "self_id": "2233",
            "group_id": "6677",
            "message_type": "group",
            "sub_type": "",
            "event": EventMessage(
                type=1,
                guild_id="5566",
                content="test channel message",  # type: ignore
                author=User(id="3344"),
                kmarkdown={
                    "raw_content": content,
                    "mention_part": [],
                    "mention_role_part": [],
                },  # type: ignore
            ),
        },
    )


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_uninfo import Scene, SceneType, Session
    from nonebot_plugin_uninfo import User as UninfoUser

    from nonebot_plugin_chatrecorder.message import serialize_message

    private_msg = "test private message"
    private_msg_id = "4455"

    channel_msg = "test channel message"
    channel_msg_id = "4456"

    async with app.test_matcher() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot, adapter=adapter, self_id="2233", name="Bot", token=""
        )

        event = fake_private_message_event(private_msg, private_msg_id)
        ctx.receive_event(bot, event)

        event = fake_channel_message_event(channel_msg, channel_msg_id)
        ctx.receive_event(bot, event)

    await check_record(
        Session(
            self_id="2233",
            adapter="Kaiheila",
            scope="Kaiheila",
            scene=Scene(id="3344", type=SceneType.PRIVATE),
            user=UninfoUser(id="3344"),
        ),
        datetime.fromtimestamp(1234000 / 1000, timezone.utc),
        "message",
        private_msg_id,
        serialize_message(bot, Message(private_msg)),
        private_msg,
    )

    await check_record(
        Session(
            self_id="2233",
            adapter="Kaiheila",
            scope="Kaiheila",
            scene=Scene(
                id="6677",
                type=SceneType.CHANNEL_TEXT,
                parent=Scene(id="5566", type=SceneType.GUILD),
            ),
            user=UninfoUser(id="3344"),
        ),
        datetime.fromtimestamp(1234000 / 1000, timezone.utc),
        "message",
        channel_msg_id,
        serialize_message(bot, Message(channel_msg)),
        channel_msg,
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_uninfo import Scene, SceneType, Session
    from nonebot_plugin_uninfo import User as UninfoUser

    from nonebot_plugin_chatrecorder.adapters.kaiheila import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot, adapter=adapter, self_id="2233", name="Bot", token=""
        )

    await record_send_msg(
        bot,
        None,
        "message_create",
        {"type": 1, "content": "test message/create", "target_id": "6677"},
        MessageCreateReturn(msg_id="4457", msg_timestamp=1234000, nonce="xxx"),
    )
    await check_record(
        Session(
            self_id="2233",
            adapter="Kaiheila",
            scope="Kaiheila",
            scene=Scene(id="6677", type=SceneType.CHANNEL_TEXT),
            user=UninfoUser(id="2233"),
        ),
        datetime.fromtimestamp(1234000 / 1000, timezone.utc),
        "message_sent",
        "4457",
        serialize_message(bot, Message("test message/create")),
        "test message/create",
    )

    await record_send_msg(
        bot,
        None,
        "directMessage_create",
        {"type": 1, "content": "test direct-message/create", "target_id": "3344"},
        MessageCreateReturn(msg_id="4458", msg_timestamp=1234000, nonce="xxx"),
    )
    await check_record(
        Session(
            self_id="2233",
            adapter="Kaiheila",
            scope="Kaiheila",
            scene=Scene(id="3344", type=SceneType.PRIVATE),
            user=UninfoUser(id="2233"),
        ),
        datetime.fromtimestamp(1234000 / 1000, timezone.utc),
        "message_sent",
        "4458",
        serialize_message(bot, Message("test direct-message/create")),
        "test direct-message/create",
    )

    await record_send_msg(
        bot,
        None,
        "message_create",
        {"type": 2, "content": "https://img.kaiheila.cn/xxx.jpg", "target_id": "6677"},
        MessageCreateReturn(msg_id="4459", msg_timestamp=1234000, nonce="xxx"),
    )
    await check_record(
        Session(
            self_id="2233",
            adapter="Kaiheila",
            scope="Kaiheila",
            scene=Scene(id="6677", type=SceneType.CHANNEL_TEXT),
            user=UninfoUser(id="2233"),
        ),
        datetime.fromtimestamp(1234000 / 1000, timezone.utc),
        "message_sent",
        "4459",
        serialize_message(
            bot, Message(MessageSegment.image("https://img.kaiheila.cn/xxx.jpg"))
        ),
        "",
    )

    card_content = json.dumps(
        [
            {
                "type": "card",
                "theme": "none",
                "size": "lg",
                "modules": [
                    {
                        "type": "section",
                        "text": {"type": "plain-text", "content": "test"},
                    },
                    {
                        "type": "container",
                        "elements": [
                            {"type": "image", "src": "https://img.kaiheila.cn/xxx.jpg"}
                        ],
                    },
                ],
            }
        ]
    )
    await record_send_msg(
        bot,
        None,
        "message_create",
        {
            "type": 10,
            "content": card_content,
            "target_id": "6677",
        },
        MessageCreateReturn(msg_id="4460", msg_timestamp=1234000, nonce="xxx"),
    )
    await check_record(
        Session(
            self_id="2233",
            adapter="Kaiheila",
            scope="Kaiheila",
            scene=Scene(id="6677", type=SceneType.CHANNEL_TEXT),
            user=UninfoUser(id="2233"),
        ),
        datetime.fromtimestamp(1234000 / 1000, timezone.utc),
        "message_sent",
        "4460",
        serialize_message(bot, Message(MessageSegment.Card(card_content))),
        "",
    )
