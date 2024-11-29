from datetime import datetime, timezone

from nonebot import get_driver
from nonebot.adapters.satori import Adapter, Bot, Message
from nonebot.adapters.satori.config import ClientInfo
from nonebot.adapters.satori.event import (
    PrivateMessageCreatedEvent,
    PublicMessageCreatedEvent,
    PublicMessageDeletedEvent,
    PublicMessageUpdatedEvent,
)
from nonebot.adapters.satori.models import (
    Channel,
    ChannelType,
    Guild,
    Login,
    LoginStatus,
    Member,
    MessageObject,
    User,
)
from nonebot.compat import type_validate_python
from nonebug.app import App

from .utils import assert_no_record, check_record


def fake_public_message_created_event(
    content: str, msg_id: str
) -> PublicMessageCreatedEvent:
    return type_validate_python(
        PublicMessageCreatedEvent,
        {
            "id": 1,
            "type": "message-created",
            "platform": "kook",
            "self_id": "2233",
            "timestamp": 17000000000,
            "channel": {"id": "6677", "type": 0, "name": "test"},
            "guild": {"id": "5566", "name": "test"},
            "user": {"id": "3344", "nick": "test"},
            "member": {
                "user": {"id": "3344", "nick": "test"},
                "nick": "test",
                "joined_at": None,
            },
            "message": {"id": msg_id, "content": content},
        },
    )


def fake_private_message_created_event(
    content: str, msg_id: str
) -> PrivateMessageCreatedEvent:
    return type_validate_python(
        PrivateMessageCreatedEvent,
        {
            "id": 1,
            "type": "message-created",
            "platform": "kook",
            "self_id": "2233",
            "timestamp": 17000000000,
            "channel": {"id": "6677", "type": 0, "name": "test"},
            "user": {"id": "3344", "nick": "test"},
            "message": {"id": msg_id, "content": content},
        },
    )


def fake_public_message_deleted_event(
    content: str, msg_id: str
) -> PublicMessageDeletedEvent:
    return type_validate_python(
        PublicMessageDeletedEvent,
        {
            "id": 1,
            "type": "message-deleted",
            "platform": "kook",
            "self_id": "2233",
            "timestamp": 17000000000,
            "channel": {"id": "6677", "type": 0, "name": "test"},
            "guild": {"id": "5566", "name": "test"},
            "user": {"id": "3344", "nick": "test"},
            "member": {
                "user": {"id": "3344", "nick": "test"},
                "nick": "test",
                "joined_at": None,
            },
            "message": {"id": msg_id, "content": content},
        },
    )


def fake_public_message_updated_event(
    content: str, msg_id: str
) -> PublicMessageUpdatedEvent:
    return type_validate_python(
        PublicMessageUpdatedEvent,
        {
            "id": 1,
            "type": "message-updated",
            "platform": "kook",
            "self_id": "2233",
            "timestamp": 17000000000,
            "channel": {"id": "6677", "type": 0, "name": "test"},
            "guild": {"id": "5566", "name": "test"},
            "user": {"id": "3344", "nick": "test"},
            "member": {
                "user": {"id": "3344", "nick": "test"},
                "nick": "test",
                "joined_at": None,
            },
            "message": {"id": msg_id, "content": content},
        },
    )


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_uninfo import Scene, SceneType, Session
    from nonebot_plugin_uninfo import User as UninfoUser

    from nonebot_plugin_chatrecorder.message import serialize_message

    public_msg = "test public message created"
    public_msg_id = "56163f81-de30-4c39-b4c4-3a205d0be9da"

    private_msg = "test private message created"
    private_msg_id = "56163f81-de30-4c39-b4c4-3a205d0be9db"

    msg_deleted_id = "56163f81-de30-4c39-b4c4-3a205d0be9dc"
    msg_updated_id = "56163f81-de30-4c39-b4c4-3a205d0be9dd"

    async with app.test_matcher() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot,
            adapter=adapter,
            self_id="2233",
            login=Login(
                user=User(
                    id="2233",
                    name="Bot",
                    avatar="https://xxx.png",
                ),
                self_id="2233",
                platform="kook",
                status=LoginStatus.ONLINE,
            ),
            info=ClientInfo(port=5140),
        )

        event = fake_public_message_created_event(public_msg, public_msg_id)
        ctx.receive_event(bot, event)

        event = fake_private_message_created_event(private_msg, private_msg_id)
        ctx.receive_event(bot, event)

        event = fake_public_message_deleted_event("msg deleted", msg_deleted_id)
        ctx.receive_event(bot, event)

        event = fake_public_message_updated_event("msg updated", msg_updated_id)
        ctx.receive_event(bot, event)

    await check_record(
        Session(
            self_id="2233",
            adapter="Satori",
            scope="Kaiheila",
            scene=Scene(
                id="6677",
                type=SceneType.CHANNEL_TEXT,
                parent=Scene(id="5566", type=SceneType.GUILD),
            ),
            user=UninfoUser(id="3344"),
        ),
        datetime.fromtimestamp(17000000000 / 1000, timezone.utc),
        "message",
        public_msg_id,
        serialize_message(bot, Message(public_msg)),
        public_msg,
    )

    await check_record(
        Session(
            self_id="2233",
            adapter="Satori",
            scope="Kaiheila",
            scene=Scene(id="3344", type=SceneType.PRIVATE),
            user=UninfoUser(id="3344"),
        ),
        datetime.fromtimestamp(17000000000 / 1000, timezone.utc),
        "message",
        private_msg_id,
        serialize_message(bot, Message(private_msg)),
        private_msg,
    )

    await assert_no_record(msg_deleted_id)
    await assert_no_record(msg_updated_id)


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_uninfo import Scene, SceneType, Session
    from nonebot_plugin_uninfo import User as UninfoUser

    from nonebot_plugin_chatrecorder.adapters.satori import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot,
            adapter=adapter,
            self_id="2233",
            login=Login(
                user=User(
                    id="2233",
                    name="Bot",
                    avatar="https://xxx.png",
                ),
                self_id="2233",
                platform="kook",
                status=LoginStatus.ONLINE,
            ),
            info=ClientInfo(port=5140),
        )

    await record_send_msg(
        bot,
        None,
        "message_create",
        {"channel_id": "6677", "content": "test"},
        [
            MessageObject(
                id="6b701984-c185-4da9-9808-549dc9947b85",
                content="test",
                channel=Channel(
                    id="6677", type=ChannelType.TEXT, name="文字频道", parent_id=None
                ),
                guild=Guild(id="5566", name=None, avatar=None),
                member=Member(
                    user=None,
                    nick="Aislinn",
                    avatar=None,
                    joined_at=None,
                ),
                user=User(
                    id="3344",
                    name="Aislinn",
                    nick=None,
                    avatar="https://img.kookapp.cn/avatars/2021-08/GjdUSjtmtD06j06j.png?x-oss-process=style/icon",
                    is_bot=None,
                ),
                created_at=None,
                updated_at=None,
            )
        ],
    )
    await check_record(
        Session(
            self_id="2233",
            adapter="Satori",
            scope="Kaiheila",
            scene=Scene(
                id="6677",
                type=SceneType.CHANNEL_TEXT,
                parent=Scene(id="5566", type=SceneType.GUILD),
            ),
            user=UninfoUser(id="2233"),
        ),
        None,
        "message_sent",
        "6b701984-c185-4da9-9808-549dc9947b85",
        serialize_message(bot, Message("test")),
        "test",
    )
