import pytest

pytest.importorskip("nonebot.adapters.kaiheila")

from datetime import datetime

from nonebot import get_driver
from nonebot.adapters.kaiheila import Adapter, Bot, Message
from nonebot.adapters.kaiheila.api.model import MessageCreateReturn
from nonebot.adapters.kaiheila.event import (
    ChannelMessageEvent,
    EventMessage,
    Extra,
    PrivateMessageEvent,
    User,
)
from nonebug.app import App

from .utils import check_record


@pytest.fixture(scope="session", autouse=True)
def load_adapters(nonebug_init: None):
    driver = get_driver()
    driver.register_adapter(Adapter)


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_chatrecorder.adapters.kaiheila import record_recv_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=Adapter(get_driver()),
            self_id="2233",
            name="Bot",
            token="",
        )

    event = PrivateMessageEvent(
        post_type="message",
        channel_type="PERSON",
        type=1,
        target_id="6677",
        author_id="3344",
        content="123",
        msg_id="4455",
        msg_timestamp=1234000,
        nonce="",
        extra=Extra(
            type=1,
            guild_id=None,
            channel_name=None,
            mention=[],
            mention_all=False,
            mention_roles=[],
            mention_here=False,
            author=None,
            body=None,
            attachments=None,
            code=None,
        ),
        user_id="3344",
        self_id="2233",
        message_type="private",
        sub_type="",
        event=EventMessage(
            type=1,
            guild_id=None,
            channel_name=None,
            content="test private message",  # type: ignore
            mention=[],
            mention_all=False,
            mention_roles=[],
            mention_here=False,
            nav_channels=[],
            author=User(id="3344"),
            kmarkdown=None,
            attachments=None,
            code=None,
        ),
    )
    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "Kaiheila",
        "kaiheila",
        "LEVEL1",
        "3344",
        None,
        None,
        datetime.utcfromtimestamp(1234000 / 1000),
        "message",
        "4455",
        serialize_message(bot, Message("test private message")),
        "test private message",
    )

    event = ChannelMessageEvent(
        post_type="message",
        channel_type="GROUP",
        type=9,
        target_id="6677",
        author_id="3344",
        content="123",
        msg_id="4456",
        msg_timestamp=1234000,
        nonce="",
        extra=Extra(
            type=1,
            guild_id="5566",
            channel_name="test",
            mention=[],
            mention_all=False,
            mention_roles=[],
            mention_here=False,
            author=None,
            body=None,
            attachments=None,
            code=None,
        ),
        user_id="3344",
        self_id="2233",
        group_id="6677",
        message_type="group",
        sub_type="",
        event=EventMessage(
            type=1,
            guild_id="5566",
            channel_name="test",
            content="test channel message",  # type: ignore
            mention=[],
            mention_all=False,
            mention_roles=[],
            mention_here=False,
            nav_channels=[],
            author=User(id="3344"),
            kmarkdown=None,
            attachments=None,
            code=None,
        ),
    )
    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "Kaiheila",
        "kaiheila",
        "LEVEL3",
        "3344",
        "6677",
        "5566",
        datetime.utcfromtimestamp(1234000 / 1000),
        "message",
        "4456",
        serialize_message(bot, Message("test channel message")),
        "test channel message",
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_chatrecorder.adapters.kaiheila import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=Adapter(get_driver()),
            self_id="2233",
            name="Bot",
            token="",
        )

    await record_send_msg(
        bot,
        None,
        "message/create",
        {"type": 1, "content": "test message/create", "target_id": "6677"},
        MessageCreateReturn(msg_id="4457", msg_timestamp=1234000, nonce="xxx"),
    )
    await check_record(
        "2233",
        "Kaiheila",
        "kaiheila",
        "LEVEL3",
        None,
        None,
        "6677",
        datetime.utcfromtimestamp(1234000 / 1000),
        "message_sent",
        "4457",
        serialize_message(bot, Message("test message/create")),
        "test message/create",
    )

    await record_send_msg(
        bot,
        None,
        "direct-message/create",
        {"type": 1, "content": "test direct-message/create", "target_id": "3344"},
        MessageCreateReturn(msg_id="4458", msg_timestamp=1234000, nonce="xxx"),
    )
    await check_record(
        "2233",
        "Kaiheila",
        "kaiheila",
        "LEVEL1",
        "3344",
        None,
        None,
        datetime.utcfromtimestamp(1234000 / 1000),
        "message_sent",
        "4458",
        serialize_message(bot, Message("test direct-message/create")),
        "test direct-message/create",
    )
