from datetime import datetime

from nonebot import get_driver
from nonebot.adapters.discord import (
    Bot,
    DirectMessageCreateEvent,
    GuildMessageCreateEvent,
    Message,
)
from nonebot.adapters.discord.api.model import (
    Channel,
    MessageFlag,
    MessageGet,
    MessageType,
    User,
)
from nonebot.adapters.discord.config import BotInfo
from nonebot.compat import type_validate_python
from nonebug.app import App

from .utils import check_record


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_chatrecorder.adapters.discord import record_recv_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=get_driver()._adapters["Discord"],
            self_id="2233",
            bot_info=BotInfo(token="1234"),
        )
    assert isinstance(bot, Bot)

    content = "test guild message"
    event = type_validate_python(
        GuildMessageCreateEvent,
        {
            "id": 11234,
            "channel_id": 5566,
            "guild_id": 6677,
            "author": User(
                **{
                    "id": 3344,
                    "username": "MyUser",
                    "discriminator": "0",
                    "avatar": "xxx",
                }
            ),
            "content": content,
            "timestamp": 123456,
            "edited_timestamp": None,
            "tts": False,
            "mention_everyone": False,
            "mentions": [],
            "mention_roles": [],
            "attachments": [],
            "embeds": [],
            "nonce": 3210,
            "pinned": False,
            "type": MessageType(0),
            "flags": MessageFlag(0),
            "referenced_message": None,
            "components": [],
            "to_me": False,
            "reply": None,
        },
    )
    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "Discord",
        "discord",
        3,
        "3344",
        "5566",
        "6677",
        datetime.utcfromtimestamp(123456),
        "message",
        "11234",
        serialize_message(bot, Message(content)),
        Message(content).extract_plain_text(),
    )

    content = "test direct message"
    event = type_validate_python(
        DirectMessageCreateEvent,
        {
            "id": 11235,
            "channel_id": 5566,
            "author": User(
                **{
                    "id": 3344,
                    "username": "bot",
                    "discriminator": "0",
                    "avatar": "xxx",
                }
            ),
            "content": content,
            "timestamp": 123456,
            "edited_timestamp": None,
            "tts": False,
            "mention_everyone": False,
            "mentions": [],
            "mention_roles": [],
            "attachments": [],
            "embeds": [],
            "nonce": 3210,
            "pinned": False,
            "type": MessageType(0),
            "flags": MessageFlag(0),
            "referenced_message": None,
            "components": [],
            "to_me": False,
            "reply": None,
        },
    )
    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "Discord",
        "discord",
        1,
        "3344",
        "5566",
        None,
        datetime.utcfromtimestamp(123456),
        "message",
        "11235",
        serialize_message(bot, Message(content)),
        Message(content).extract_plain_text(),
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_chatrecorder.adapters.discord import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=get_driver()._adapters["Discord"],
            self_id="2233",
            bot_info=BotInfo(token="1234"),
        )
        assert isinstance(bot, Bot)

        content = "test create guild message"
        ctx.should_call_api(
            "get_channel",
            {"channel_id": 5566},
            type_validate_python(
                Channel,
                {
                    "id": 5566,
                    "type": 0,
                    "guild_id": 6677,
                    "position": 1,
                    "permission_overwrites": [],
                    "name": "test",
                    "topic": "test",
                    "nsfw": False,
                    "rate_limit_per_user": 0,
                    "parent_id": 6678,
                },
            ),
        )
        await record_send_msg(
            bot,
            None,
            "create_message",
            {
                "channel_id": 5566,
                "nonce": None,
                "tts": False,
                "allowed_mentions": None,
                "content": content,
            },
            type_validate_python(
                MessageGet,
                {
                    "id": 11236,
                    "channel_id": 5566,
                    "author": User(
                        **{
                            "id": 2233,
                            "username": "mybot",
                            "discriminator": "0",
                            "avatar": "xxx",
                        }
                    ),
                    "content": content,
                    "timestamp": 123456,
                    "edited_timestamp": None,
                    "tts": False,
                    "mention_everyone": False,
                    "mentions": [],
                    "mention_roles": [],
                    "attachments": [],
                    "embeds": [],
                    "pinned": False,
                    "type": 0,
                },
            ),
        )
        await check_record(
            "2233",
            "Discord",
            "discord",
            3,
            None,
            "5566",
            "6677",
            datetime.utcfromtimestamp(123456),
            "message_sent",
            "11236",
            serialize_message(bot, Message(content)),
            Message(content).extract_plain_text(),
        )

        content = "test create direct message"
        ctx.should_call_api(
            "get_channel",
            {"channel_id": 5555},
            type_validate_python(
                Channel,
                {
                    "id": 5555,
                    "type": 1,
                    "position": 1,
                    "permission_overwrites": [],
                    "name": "test",
                    "topic": "test",
                    "nsfw": False,
                    "rate_limit_per_user": 0,
                    "parent_id": 5554,
                    "recipients": [
                        User(
                            **{
                                "id": 3344,
                                "username": "MyUser",
                                "discriminator": "0",
                                "avatar": "xxx",
                            }
                        )
                    ],
                },
            ),
        )
        await record_send_msg(
            bot,
            None,
            "create_message",
            {
                "channel_id": 5555,
                "nonce": None,
                "tts": False,
                "allowed_mentions": None,
                "content": content,
            },
            type_validate_python(
                MessageGet,
                {
                    "id": 11237,
                    "channel_id": 5555,
                    "author": User(
                        **{
                            "id": 2233,
                            "username": "mybot",
                            "discriminator": "0",
                            "avatar": "xxx",
                        }
                    ),
                    "content": content,
                    "timestamp": 123456,
                    "edited_timestamp": None,
                    "tts": False,
                    "mention_everyone": False,
                    "mentions": [],
                    "mention_roles": [],
                    "attachments": [],
                    "embeds": [],
                    "pinned": False,
                    "type": 0,
                },
            ),
        )
        await check_record(
            "2233",
            "Discord",
            "discord",
            1,
            "3344",
            "5555",
            None,
            datetime.utcfromtimestamp(123456),
            "message_sent",
            "11237",
            serialize_message(bot, Message(content)),
            Message(content).extract_plain_text(),
        )
