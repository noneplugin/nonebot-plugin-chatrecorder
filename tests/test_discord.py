from datetime import datetime, timezone

from nonebot import get_driver
from nonebot.adapters.discord import (
    Adapter,
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


def fake_guild_message_event(content: str, msg_id: int) -> GuildMessageCreateEvent:
    return type_validate_python(
        GuildMessageCreateEvent,
        {
            "id": msg_id,
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


def fake_direct_message_event(content: str, msg_id: int) -> DirectMessageCreateEvent:
    return type_validate_python(
        DirectMessageCreateEvent,
        {
            "id": msg_id,
            "channel_id": 5566,
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


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_uninfo import Scene, SceneType, Session
    from nonebot_plugin_uninfo import User as UninfoUser

    from nonebot_plugin_chatrecorder.adapters.discord import record_recv_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    guild_msg = "test guild message"
    guild_msg_id = 11234

    direct_msg = "test direct message"
    direct_msg_id = 11235

    async with app.test_api() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot, adapter=adapter, self_id="2233", bot_info=BotInfo(token="1234")
        )

    event = fake_guild_message_event(guild_msg, guild_msg_id)
    session = Session(
        self_id="2233",
        adapter="Discord",
        scope="Discord",
        scene=Scene(
            id="5566",
            type=SceneType.CHANNEL_TEXT,
            parent=Scene(id="6677", type=SceneType.GUILD),
        ),
        user=UninfoUser(id="3344"),
    )
    await record_recv_msg(event, session)
    await check_record(
        session,
        datetime.fromtimestamp(123456, timezone.utc),
        "message",
        str(guild_msg_id),
        serialize_message(bot, Message(guild_msg)),
        guild_msg,
    )

    event = fake_direct_message_event(direct_msg, direct_msg_id)
    session = Session(
        self_id="2233",
        adapter="Discord",
        scope="Discord",
        scene=Scene(id="5566", type=SceneType.PRIVATE),
        user=UninfoUser(id="3344"),
    )
    await record_recv_msg(event, session)
    await check_record(
        session,
        datetime.fromtimestamp(123456, timezone.utc),
        "message",
        str(direct_msg_id),
        serialize_message(bot, Message(direct_msg)),
        direct_msg,
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_uninfo import Scene, SceneType, Session
    from nonebot_plugin_uninfo import User as UninfoUser

    from nonebot_plugin_chatrecorder.adapters.discord import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot, adapter=adapter, self_id="2233", bot_info=BotInfo(token="1234")
        )

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
            Session(
                self_id="2233",
                adapter="Discord",
                scope="Discord",
                scene=Scene(
                    id="5566",
                    type=SceneType.CHANNEL_TEXT,
                    parent=Scene(id="6677", type=SceneType.GUILD),
                ),
                user=UninfoUser(id="2233"),
            ),
            datetime.fromtimestamp(123456, timezone.utc),
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
            Session(
                self_id="2233",
                adapter="Discord",
                scope="Discord",
                scene=Scene(id="5555", type=SceneType.PRIVATE),
                user=UninfoUser(id="2233"),
            ),
            datetime.fromtimestamp(123456, timezone.utc),
            "message_sent",
            "11237",
            serialize_message(bot, Message(content)),
            Message(content).extract_plain_text(),
        )
