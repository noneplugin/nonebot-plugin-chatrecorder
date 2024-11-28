from datetime import datetime, timedelta, timezone

from nonebot import get_driver
from nonebot.adapters.qq import Adapter, Bot, Message
from nonebot.adapters.qq.config import BotInfo
from nonebot.adapters.qq.event import (
    C2CMessageCreateEvent,
    DirectMessageCreateEvent,
    EventType,
    GroupAtMessageCreateEvent,
    MessageCreateEvent,
)
from nonebot.adapters.qq.models import (
    FriendAuthor,
    GroupMemberAuthor,
    PostC2CMessagesReturn,
    PostGroupMessagesReturn,
    User,
)
from nonebot.adapters.qq.models import Message as GuildMessage
from nonebug import App

from .utils import check_record


def fake_message_create_event(content: str, id: str) -> MessageCreateEvent:
    return MessageCreateEvent(
        __type__=EventType.MESSAGE_CREATE,
        id=id,
        timestamp=datetime(
            2023, 7, 30, 8, 0, 0, 0, tzinfo=timezone(timedelta(hours=8))
        ),
        channel_id="6677",
        guild_id="5566",
        author=User(id="3344"),
        content=content,
    )


def fake_direct_message_create_event(content: str, id: str) -> DirectMessageCreateEvent:
    return DirectMessageCreateEvent(
        __type__=EventType.DIRECT_MESSAGE_CREATE,
        id=id,
        timestamp=datetime(
            2023, 7, 30, 8, 0, 0, 0, tzinfo=timezone(timedelta(hours=8))
        ),
        channel_id="6677",
        guild_id="5566",
        author=User(id="3344"),
        content=content,
    )


def fake_group_at_message_create_event(
    content: str, id: str
) -> GroupAtMessageCreateEvent:
    return GroupAtMessageCreateEvent(
        __type__=EventType.GROUP_AT_MESSAGE_CREATE,
        id=id,
        timestamp="2023-11-06T13:37:18+08:00",
        group_openid="195747FDF0D845E98CF3886C5C7ED328",
        author=GroupMemberAuthor(
            id="3344", member_openid="8BE608110EAA4328A1883DEF239F5580"
        ),
        content=content,
    )


def fake_c2c_message_create_event(content: str, id: str) -> C2CMessageCreateEvent:
    return C2CMessageCreateEvent(
        __type__=EventType.C2C_MESSAGE_CREATE,
        id=id,
        timestamp="2023-11-06T13:37:18+08:00",
        author=FriendAuthor(id="3344", user_openid="451368C569A1401D87172E9435EE8663"),
        content=content,
    )


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_chatrecorder.message import serialize_message

    msg = "test message create event"
    msg_id = "1234"

    direct_msg = "test direct message create event"
    direct_msg_id = "1235"

    group_at_msg = "test group at message create event"
    group_at_msg_id = "1236"

    c2c_msg = "test c2c message create event"
    c2c_msg_id = "1237"

    async with app.test_matcher() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot,
            adapter=adapter,
            self_id="2233",
            bot_info=BotInfo(id="2233", token="", secret=""),
        )

        event = fake_message_create_event(msg, msg_id)
        ctx.receive_event(bot, event)

        event = fake_direct_message_create_event(direct_msg, direct_msg_id)
        ctx.receive_event(bot, event)

        event = fake_group_at_message_create_event(group_at_msg, group_at_msg_id)
        ctx.receive_event(bot, event)

        event = fake_c2c_message_create_event(c2c_msg, c2c_msg_id)
        ctx.receive_event(bot, event)

    await check_record(
        "2233",
        "QQ",
        "qqguild",
        3,
        "3344",
        "6677",
        "5566",
        datetime(2023, 7, 30, 0, 0, 0, 0, tzinfo=timezone.utc),
        "message",
        msg_id,
        serialize_message(bot, Message(msg)),
        msg,
    )

    await check_record(
        "2233",
        "QQ",
        "qqguild",
        1,
        "3344",
        "6677",
        "5566",
        datetime(2023, 7, 30, 0, 0, 0, 0, tzinfo=timezone.utc),
        "message",
        direct_msg_id,
        serialize_message(bot, Message(direct_msg)),
        direct_msg,
    )

    await check_record(
        "2233",
        "QQ",
        "qq",
        2,
        "8BE608110EAA4328A1883DEF239F5580",
        "195747FDF0D845E98CF3886C5C7ED328",
        None,
        datetime.fromisoformat("2023-11-06T13:37:18+08:00"),
        "message",
        group_at_msg_id,
        serialize_message(bot, Message(group_at_msg)),
        group_at_msg,
    )

    await check_record(
        "2233",
        "QQ",
        "qq",
        1,
        "451368C569A1401D87172E9435EE8663",
        None,
        None,
        datetime.fromisoformat("2023-11-06T13:37:18+08:00"),
        "message",
        c2c_msg_id,
        serialize_message(bot, Message(c2c_msg)),
        c2c_msg,
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""

    from nonebot_plugin_chatrecorder.adapters.qq import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot,
            adapter=adapter,
            self_id="2233",
            bot_info=BotInfo(id="2233", token="", secret=""),
        )

    await record_send_msg(
        bot,
        None,
        "post_messages",
        {
            "channel_id": "6677",
            "msg_id": "1236",
            "content": "test post_messages",
            "event_id": None,
        },
        GuildMessage(
            id="1238",
            channel_id="6677",
            guild_id="5566",
            content="test post_messages",
            timestamp=datetime(
                2023, 7, 30, 8, 0, 0, 0, tzinfo=timezone(timedelta(hours=8))
            ),
            author=User(id="3344"),
        ),
    )
    await check_record(
        "2233",
        "QQ",
        "qqguild",
        3,
        None,
        "6677",
        "5566",
        datetime(2023, 7, 30, 0, 0, 0, 0, tzinfo=timezone.utc),
        "message_sent",
        "1238",
        serialize_message(bot, Message("test post_messages")),
        "test post_messages",
    )

    await record_send_msg(
        bot,
        None,
        "post_dms_messages",
        {
            "guild_id": "5566",
            "msg_id": "1239",
            "content": "test post_dms_messages",
            "event_id": None,
        },
        GuildMessage(
            id="1239",
            channel_id="",
            guild_id="5566",
            content="test post_dms_messages",
            timestamp=datetime(
                2023, 7, 30, 8, 0, 0, 0, tzinfo=timezone(timedelta(hours=8))
            ),
            author=User(id="3344"),
        ),
    )
    await check_record(
        "2233",
        "QQ",
        "qqguild",
        1,
        None,
        None,
        "5566",
        datetime(2023, 7, 30, 0, 0, 0, 0, tzinfo=timezone.utc),
        "message_sent",
        "1239",
        serialize_message(bot, Message("test post_dms_messages")),
        "test post_dms_messages",
    )

    await record_send_msg(
        bot,
        None,
        "post_c2c_messages",
        {
            "openid": "87E469B751CD4520B0B18D826CC94B71",
            "msg_type": 1,
            "msg_id": "1240",
            "msg_seq": 0,
            "content": "test post_c2c_messages",
            "event_id": None,
        },
        PostC2CMessagesReturn(
            id="1241",
            timestamp=datetime(
                2023, 7, 30, 8, 0, 0, 0, tzinfo=timezone(timedelta(hours=8))
            ),
        ),
    )
    await check_record(
        "2233",
        "QQ",
        "qq",
        1,
        "87E469B751CD4520B0B18D826CC94B71",
        None,
        None,
        datetime(2023, 7, 30, 0, 0, 0, 0, tzinfo=timezone.utc),
        "message_sent",
        "1241",
        serialize_message(bot, Message("test post_c2c_messages")),
        "test post_c2c_messages",
    )

    await record_send_msg(
        bot,
        None,
        "post_group_messages",
        {
            "group_openid": "1CC5DF4814E54834B0A7F5D553BB25CC",
            "msg_type": 1,
            "msg_id": "1242",
            "msg_seq": 0,
            "content": "test post_group_messages",
            "event_id": None,
        },
        PostGroupMessagesReturn(
            id="1243",
            timestamp=datetime(
                2023, 7, 30, 8, 0, 0, 0, tzinfo=timezone(timedelta(hours=8))
            ),
        ),
    )
    await check_record(
        "2233",
        "QQ",
        "qq",
        2,
        None,
        "1CC5DF4814E54834B0A7F5D553BB25CC",
        None,
        datetime(2023, 7, 30, 0, 0, 0, 0, tzinfo=timezone.utc),
        "message_sent",
        "1243",
        serialize_message(bot, Message("test post_group_messages")),
        "test post_group_messages",
    )


def test_message_deserialize():
    """测试消息反序列化"""
    from nonebot.adapters.qq import Message, MessageSegment
    from nonebot.adapters.qq.message import Embed
    from nonebot.adapters.qq.models import MessageArk, MessageEmbed
    from nonebot.compat import type_validate_python

    msg = type_validate_python(Message, [{"type": "text", "data": {"text": "test"}}])
    assert msg == Message(MessageSegment.text("test"))

    msg = type_validate_python(Message, [{"type": "image", "data": {"url": "test"}}])
    assert msg == Message(MessageSegment.image("test"))

    msg = type_validate_python(
        Message, [{"type": "file_image", "data": {"content": b"\x89PNG\r"}}]
    )
    assert msg == Message(MessageSegment.file_image(b"\x89PNG\r"))

    msg = type_validate_python(
        Message, [{"type": "ark", "data": {"ark": {"template_id": 1, "kv": []}}}]
    )
    assert msg == Message(MessageSegment.ark(MessageArk(template_id=1, kv=[])))

    seg = type_validate_python(
        Embed, {"type": "embed", "data": {"embed": {"prompt": "test"}}}
    )
    assert seg == MessageSegment.embed(MessageEmbed(prompt="test"))
