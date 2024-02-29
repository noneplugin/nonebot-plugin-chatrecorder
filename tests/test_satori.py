from datetime import datetime

from nonebot import get_driver
from nonebot.adapters.satori import Adapter, Bot, Message
from nonebot.adapters.satori.config import ClientInfo
from nonebot.adapters.satori.event import PublicMessageCreatedEvent
from nonebot.adapters.satori.models import Channel, ChannelType, Guild, User
from nonebot.adapters.satori.models import InnerMember as Member
from nonebot.adapters.satori.models import InnerMessage as SatoriMessage
from nonebot.adapters.satori.utils import Element
from nonebot.compat import type_validate_python
from nonebug.app import App

from .utils import check_record


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_chatrecorder.adapters.satori import record_recv_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=Adapter(get_driver()),
            self_id="2233",
            platform="kook",
            info=ClientInfo(port=5140),
        )
    assert isinstance(bot, Bot)

    event = type_validate_python(
        PublicMessageCreatedEvent,
        {
            "id": 4,
            "type": "message-created",
            "platform": "kook",
            "self_id": "2233",
            "timestamp": 17000000000,
            "argv": None,
            "button": None,
            "channel": {
                "id": "6677",
                "type": 0,
                "name": "文字频道",
                "parent_id": None,
            },
            "guild": {"id": "5566", "name": None, "avatar": None},
            "login": None,
            "member": {
                "user": None,
                "name": None,
                "nick": "Aislinn",
                "avatar": None,
                "joined_at": None,
            },
            "message": {
                "id": "56163f81-de30-4c39-b4c4-3a205d0be9da",
                "content": [
                    {
                        "type": "text",
                        "attrs": {"text": "test"},
                        "children": [],
                        "source": None,
                    }
                ],
                "channel": None,
                "guild": None,
                "member": {
                    "user": {
                        "id": "3344",
                        "name": "Aislinn",
                        "nick": None,
                        "avatar": "https://img.kookapp.cn/avatars/2021-08/GjdUSjtmtD06j06j.png?x-oss-process=style/icon",
                        "is_bot": None,
                        "username": "Aislinn",
                        "user_id": "3344",
                        "discriminator": "4261",
                    },
                    "name": None,
                    "nick": "Aislinn",
                    "avatar": None,
                    "joined_at": None,
                },
                "user": {
                    "id": "3344",
                    "name": "Aislinn",
                    "nick": None,
                    "avatar": "https://img.kookapp.cn/avatars/2021-08/GjdUSjtmtD06j06j.png?x-oss-process=style/icon",
                    "is_bot": None,
                    "username": "Aislinn",
                    "user_id": "3344",
                    "discriminator": "4261",
                },
                "created_at": None,
                "updated_at": None,
                "message_id": "56163f81-de30-4c39-b4c4-3a205d0be9da",
                "elements": [
                    {"type": "text", "attrs": {"content": "test"}, "children": []}
                ],
                "timestamp": 1700474858446,
            },
            "operator": None,
            "role": None,
            "user": {
                "id": "3344",
                "name": "Aislinn",
                "nick": None,
                "avatar": "https://img.kookapp.cn/avatars/2021-08/GjdUSjtmtD06j06j.png?x-oss-process=style/icon",
                "is_bot": None,
                "username": "Aislinn",
                "user_id": "3344",
                "discriminator": "4261",
            },
            "_type": "kook",
        },
    )
    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "Satori",
        "kaiheila",
        3,
        "3344",
        "6677",
        "5566",
        datetime.utcfromtimestamp(17000000000 / 1000),
        "message",
        "56163f81-de30-4c39-b4c4-3a205d0be9da",
        serialize_message(bot, Message("test")),
        "test",
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_chatrecorder.adapters.satori import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=Adapter(get_driver()),
            self_id="2233",
            platform="kook",
            info=ClientInfo(port=5140),
        )
    assert isinstance(bot, Bot)

    await record_send_msg(
        bot,
        None,
        "message_create",
        {"channel_id": "6677", "content": "test"},
        [
            SatoriMessage(
                id="6b701984-c185-4da9-9808-549dc9947b85",
                content=[
                    Element(
                        type="text", attrs={"text": "test"}, children=[], source=None
                    )
                ],
                channel=Channel(
                    id="6677", type=ChannelType.TEXT, name="文字频道", parent_id=None
                ),
                guild=Guild(id="5566", name=None, avatar=None),
                member=Member(
                    user=None,
                    name=None,
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
        "2233",
        "Satori",
        "kook",
        3,
        None,
        "6677",
        "5566",
        None,
        "message_sent",
        "6b701984-c185-4da9-9808-549dc9947b85",
        serialize_message(bot, Message("test")),
        "test",
    )
