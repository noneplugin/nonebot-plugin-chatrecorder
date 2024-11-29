from datetime import datetime, timezone

from nonebot import get_driver
from nonebot.adapters.feishu import (
    Adapter,
    Bot,
    EventHeader,
    GroupMessageEvent,
    GroupMessageEventDetail,
    Message,
    PrivateMessageEvent,
    PrivateMessageEventDetail,
    UserId,
)
from nonebot.adapters.feishu.config import BotConfig
from nonebot.adapters.feishu.models import (
    BotInfo,
    GroupEventMessage,
    PrivateEventMessage,
    Sender,
)
from nonebot.compat import type_validate_python
from nonebug.app import App

from .utils import check_record

BOT_CONFIG = BotConfig(app_id="114", app_secret="514", verification_token="1919810")
BOT_INFO = type_validate_python(
    BotInfo,
    {
        "activate_status": 2,
        "app_name": "name",
        "avatar_url": "https://s1-imfile.feishucdn.com/test.jpg",
        "ip_white_list": [],
        "open_id": "ou_123456",
    },
)


def fake_header() -> EventHeader:
    return EventHeader(
        event_id="114514",
        event_type="im.message.receive_v1",
        create_time="123456000",
        token="token",
        app_id="app_id",
        tenant_key="tenant_key",
        resource_id=None,
        user_list=None,
    )


def fake_sender() -> Sender:
    return Sender(
        sender_id=UserId(
            open_id="3344",
            user_id="on_111",
            union_id="on_222",
        ),
        tenant_key="tenant_key",
        sender_type="user",
    )


def fake_private_message_event(
    msg_type: str, content: str, message_id: str
) -> PrivateMessageEvent:
    return PrivateMessageEvent(
        schema="2.0",
        header=fake_header(),
        event=PrivateMessageEventDetail(
            sender=fake_sender(),
            message=PrivateEventMessage(
                chat_type="p2p",
                message_id=message_id,
                root_id="om_222",
                parent_id="om_333",
                create_time="123456000",
                chat_id="oc_123",
                message_type=msg_type,
                content=content,
                mentions=None,
            ),
        ),
        reply=None,
    )  # type: ignore


def fake_group_message_event(
    msg_type: str, content: str, message_id: str
) -> GroupMessageEvent:
    return GroupMessageEvent(
        schema="2.0",
        header=fake_header(),
        event=GroupMessageEventDetail(
            sender=fake_sender(),
            message=GroupEventMessage(
                chat_type="group",
                message_id=message_id,
                root_id="om_222",
                parent_id="om_333",
                create_time="123456000",
                chat_id="1122",
                message_type=msg_type,
                content=content,
                mentions=None,
            ),
        ),
        reply=None,
    )  # type: ignore


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_uninfo import Scene, SceneType, Session, User

    from nonebot_plugin_chatrecorder.message import serialize_message

    msg_type = "text"
    content = '{"text": "test"}'
    private_msg_id = "om_1"
    group_msg_id = "om_2"
    message = Message.deserialize(content, None, msg_type)

    async with app.test_matcher() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot,
            adapter=adapter,
            self_id="2233",
            bot_config=BOT_CONFIG,
            bot_info=BOT_INFO,
        )

        event = fake_private_message_event(msg_type, content, private_msg_id)
        ctx.receive_event(bot, event)

        event = fake_group_message_event(msg_type, content, group_msg_id)
        ctx.receive_event(bot, event)

    await check_record(
        Session(
            self_id="2233",
            adapter="Feishu",
            scope="Feishu",
            scene=Scene(id="3344", type=SceneType.PRIVATE),
            user=User(id="3344"),
        ),
        datetime.fromtimestamp(123456000 / 1000, timezone.utc),
        "message",
        private_msg_id,
        serialize_message(bot, message),
        message.extract_plain_text(),
    )

    await check_record(
        Session(
            self_id="2233",
            adapter="Feishu",
            scope="Feishu",
            scene=Scene(id="1122", type=SceneType.GROUP),
            user=User(id="3344"),
        ),
        datetime.fromtimestamp(123456000 / 1000, timezone.utc),
        "message",
        group_msg_id,
        serialize_message(bot, message),
        message.extract_plain_text(),
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_uninfo import Scene, SceneType, Session, User

    from nonebot_plugin_chatrecorder.adapters.feishu import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot,
            adapter=adapter,
            self_id="2233",
            bot_config=BOT_CONFIG,
            bot_info=BOT_INFO,
        )

        msg_type = "text"
        content = '{"text": "test"}'
        message = Message.deserialize(content, None, msg_type)

        ctx.should_call_api(
            "im/v1/chats/oc_123",
            {"method": "GET", "query": {"user_id_type": "open_id"}},
            {
                "code": 0,
                "msg": "success",
                "data": {
                    "chat_mode": "group",
                    "name": "test",
                    "owner_id": "3344",
                    "owner_id_type": "open_id",
                },
            },
        )
        await record_send_msg(
            bot,
            None,
            "im/v1/messages",
            {
                "method": "POST",
                "query": {"receive_id_type": "chat_id"},
                "body": {
                    "receive_id": "oc_123",
                    "content": content,
                    "msg_type": msg_type,
                },
            },
            {
                "code": 0,
                "msg": "success",
                "data": {
                    "body": {"content": content},
                    "chat_id": "oc_123",
                    "create_time": "123456000",
                    "mentions": [],
                    "message_id": "om_3",
                    "msg_type": msg_type,
                    "sender": {
                        "id": "2233",
                        "id_type": "app_id",
                        "sender_type": "app",
                        "tenant_key": "tenant_key",
                    },
                },
            },
        )
        await check_record(
            Session(
                self_id="2233",
                adapter="Feishu",
                scope="Feishu",
                scene=Scene(id="oc_123", type=SceneType.GROUP),
                user=User(id="2233"),
            ),
            datetime.fromtimestamp(123456000 / 1000, timezone.utc),
            "message_sent",
            "om_3",
            serialize_message(bot, message),
            message.extract_plain_text(),
        )

        ctx.should_call_api(
            "im/v1/chats/oc_456",
            {"method": "GET", "query": {"user_id_type": "open_id"}},
            {
                "code": 0,
                "msg": "success",
                "data": {
                    "chat_mode": "p2p",
                    "name": "test",
                    "owner_id": "3344",
                    "owner_id_type": "open_id",
                },
            },
        )
        await record_send_msg(
            bot,
            None,
            "im/v1/messages",
            {
                "method": "POST",
                "query": {"receive_id_type": "open_id"},
                "body": {
                    "receive_id": "3344",
                    "content": content,
                    "msg_type": msg_type,
                },
            },
            {
                "code": 0,
                "msg": "success",
                "data": {
                    "body": {"content": content},
                    "chat_id": "oc_456",
                    "create_time": "123456000",
                    "mentions": [],
                    "message_id": "om_4",
                    "msg_type": msg_type,
                    "sender": {
                        "id": "2233",
                        "id_type": "app_id",
                        "sender_type": "app",
                        "tenant_key": "tenant_key",
                    },
                },
            },
        )
        await check_record(
            Session(
                self_id="2233",
                adapter="Feishu",
                scope="Feishu",
                scene=Scene(id="3344", type=SceneType.PRIVATE),
                user=User(id="2233"),
            ),
            datetime.fromtimestamp(123456000 / 1000, timezone.utc),
            "message_sent",
            "om_4",
            serialize_message(bot, message),
            message.extract_plain_text(),
        )

        await record_send_msg(
            bot,
            None,
            "im/v1/messages/om_123456/reply",
            {
                "method": "POST",
                "body": {
                    "content": content,
                    "msg_type": msg_type,
                },
            },
            {
                "code": 0,
                "msg": "success",
                "data": {
                    "body": {"content": content},
                    "chat_id": "oc_123",
                    "create_time": "123456000",
                    "mentions": [],
                    "message_id": "om_5",
                    "msg_type": msg_type,
                    "sender": {
                        "id": "2233",
                        "id_type": "app_id",
                        "sender_type": "app",
                        "tenant_key": "tenant_key",
                    },
                },
            },
        )
        await check_record(
            Session(
                self_id="2233",
                adapter="Feishu",
                scope="Feishu",
                scene=Scene(id="oc_123", type=SceneType.GROUP),
                user=User(id="2233"),
            ),
            datetime.fromtimestamp(123456000 / 1000, timezone.utc),
            "message_sent",
            "om_5",
            serialize_message(bot, message),
            message.extract_plain_text(),
        )

        await record_send_msg(
            bot,
            None,
            "im/v1/messages/om_123456/reply",
            {
                "method": "POST",
                "body": {
                    "content": content,
                    "msg_type": msg_type,
                },
            },
            {
                "code": 0,
                "msg": "success",
                "data": {
                    "body": {"content": content},
                    "chat_id": "oc_456",
                    "create_time": "123456000",
                    "mentions": [],
                    "message_id": "om_6",
                    "msg_type": msg_type,
                    "sender": {
                        "id": "2233",
                        "id_type": "app_id",
                        "sender_type": "app",
                        "tenant_key": "tenant_key",
                    },
                },
            },
        )
        await check_record(
            Session(
                self_id="2233",
                adapter="Feishu",
                scope="Feishu",
                scene=Scene(id="3344", type=SceneType.PRIVATE),
                user=User(id="2233"),
            ),
            datetime.fromtimestamp(123456000 / 1000, timezone.utc),
            "message_sent",
            "om_6",
            serialize_message(bot, message),
            message.extract_plain_text(),
        )
