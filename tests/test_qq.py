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
    from nonebot_plugin_uninfo import Scene, SceneType, Session
    from nonebot_plugin_uninfo import User as UninfoUser

    from nonebot_plugin_chatrecorder.adapters.qq import record_recv_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    msg = "test message create event"
    msg_id = "1234"

    direct_msg = "test direct message create event"
    direct_msg_id = "1235"

    group_at_msg = "test group at message create event"
    group_at_msg_id = "1236"

    c2c_msg = "test c2c message create event"
    c2c_msg_id = "1237"

    async with app.test_api() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot,
            adapter=adapter,
            self_id="2233",
            bot_info=BotInfo(id="2233", token="", secret=""),
        )

    event = fake_message_create_event(msg, msg_id)
    session = Session(
        self_id="2233",
        adapter="QQ",
        scope="QQAPI",
        scene=Scene(
            id="6677",
            type=SceneType.CHANNEL_TEXT,
            parent=Scene(id="5566", type=SceneType.GUILD),
        ),
        user=UninfoUser(id="3344"),
    )
    await record_recv_msg(event, session)
    await check_record(
        session,
        datetime(2023, 7, 30, 0, 0, 0, 0, tzinfo=timezone.utc),
        "message",
        msg_id,
        serialize_message(bot, Message(msg)),
        msg,
    )

    event = fake_direct_message_create_event(direct_msg, direct_msg_id)
    session = Session(
        self_id="2233",
        adapter="QQ",
        scope="QQAPI",
        scene=Scene(
            id="3344",
            type=SceneType.PRIVATE,
            parent=Scene(id="5566", type=SceneType.GUILD),
        ),
        user=UninfoUser(id="3344"),
    )
    await record_recv_msg(event, session)
    await check_record(
        session,
        datetime(2023, 7, 30, 0, 0, 0, 0, tzinfo=timezone.utc),
        "message",
        direct_msg_id,
        serialize_message(bot, Message(direct_msg)),
        direct_msg,
    )

    event = fake_group_at_message_create_event(group_at_msg, group_at_msg_id)
    session = Session(
        self_id="2233",
        adapter="QQ",
        scope="QQAPI",
        scene=Scene(id="195747FDF0D845E98CF3886C5C7ED328", type=SceneType.GROUP),
        user=UninfoUser(id="8BE608110EAA4328A1883DEF239F5580"),
    )
    await record_recv_msg(event, session)
    await check_record(
        session,
        datetime.fromisoformat("2023-11-06T13:37:18+08:00"),
        "message",
        group_at_msg_id,
        serialize_message(bot, Message(group_at_msg)),
        group_at_msg,
    )

    event = fake_c2c_message_create_event(c2c_msg, c2c_msg_id)
    session = Session(
        self_id="2233",
        adapter="QQ",
        scope="QQAPI",
        scene=Scene(id="451368C569A1401D87172E9435EE8663", type=SceneType.PRIVATE),
        user=UninfoUser(id="451368C569A1401D87172E9435EE8663"),
    )
    await record_recv_msg(event, session)
    await check_record(
        session,
        datetime.fromisoformat("2023-11-06T13:37:18+08:00"),
        "message",
        c2c_msg_id,
        serialize_message(bot, Message(c2c_msg)),
        c2c_msg,
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_uninfo import Scene, SceneType, Session
    from nonebot_plugin_uninfo import User as UninfoUser

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
        Session(
            self_id="2233",
            adapter="QQ",
            scope="QQAPI",
            scene=Scene(
                id="6677",
                type=SceneType.CHANNEL_TEXT,
                parent=Scene(id="5566", type=SceneType.GUILD),
            ),
            user=UninfoUser(id="2233"),
        ),
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
        Session(
            self_id="2233",
            adapter="QQ",
            scope="QQAPI",
            scene=Scene(
                id="3344",
                type=SceneType.PRIVATE,
                parent=Scene(id="5566", type=SceneType.GUILD),
            ),
            user=UninfoUser(id="2233"),
        ),
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
        Session(
            self_id="2233",
            adapter="QQ",
            scope="QQAPI",
            scene=Scene(id="87E469B751CD4520B0B18D826CC94B71", type=SceneType.PRIVATE),
            user=UninfoUser(id="2233"),
        ),
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
        Session(
            self_id="2233",
            adapter="QQ",
            scope="QQAPI",
            scene=Scene(id="1CC5DF4814E54834B0A7F5D553BB25CC", type=SceneType.GROUP),
            user=UninfoUser(id="2233"),
        ),
        datetime(2023, 7, 30, 0, 0, 0, 0, tzinfo=timezone.utc),
        "message_sent",
        "1243",
        serialize_message(bot, Message("test post_group_messages")),
        "test post_group_messages",
    )
