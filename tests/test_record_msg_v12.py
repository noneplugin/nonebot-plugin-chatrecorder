import pytest
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from nonebot.adapters.onebot.v12 import Message

from nonebug.app import App

from .utils import (
    fake_group_message_event_v12,
    fake_private_message_event_v12,
    fake_channel_message_event_v12,
)

USER_ID = "111111"
GROUP_ID = "222222"
GUILD_ID = "333333"
CHANNEL_ID = "444444"


@pytest.mark.asyncio
async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""

    from nonebot_plugin_chatrecorder import record_recv_msg_v12
    from nonebot.adapters.onebot.v12 import Bot, Message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(base=Bot, platform="qq")
    assert isinstance(bot, Bot)

    time = datetime.utcfromtimestamp(1000000)

    message_id = "11451411111"
    message = Message("test group message")
    event = fake_group_message_event_v12(
        time=time,
        user_id=USER_ID,
        group_id=GROUP_ID,
        message_id=message_id,
        message=message,
        alt_message=message.extract_plain_text(),
    )
    await record_recv_msg_v12(bot, event)
    await check_record(
        time,
        message_id,
        "group",
        message,
        bot.platform,
        user_id=USER_ID,
        group_id=GROUP_ID,
    )

    message_id = "11451422222"
    message = Message("test private message")
    event = fake_private_message_event_v12(
        time=time,
        user_id=USER_ID,
        message_id=message_id,
        message=message,
        alt_message=message.extract_plain_text(),
    )
    await record_recv_msg_v12(bot, event)
    await check_record(
        time,
        message_id,
        "private",
        message,
        bot.platform,
        user_id=USER_ID,
    )

    message_id = "11451433333"
    message = Message("test channel message")
    event = fake_channel_message_event_v12(
        time=time,
        user_id=USER_ID,
        guild_id=GUILD_ID,
        channel_id=CHANNEL_ID,
        message_id=message_id,
        message=message,
        alt_message=message.extract_plain_text(),
    )
    await record_recv_msg_v12(bot, event)
    await check_record(
        time,
        message_id,
        "channel",
        message,
        bot.platform,
        user_id=USER_ID,
        guild_id=GUILD_ID,
        channel_id=CHANNEL_ID,
    )


@pytest.mark.asyncio
async def test_record_send_msg(app: App):
    """测试记录发送的消息"""

    from nonebot_plugin_chatrecorder import record_send_msg_v12
    from nonebot.adapters.onebot.v12 import Bot, Message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(base=Bot, platform="qq")
    assert isinstance(bot, Bot)

    time = 1000000

    message_id = "11451444444"
    message = Message("test call_api send_message group message")
    await record_send_msg_v12(
        bot,
        None,
        "send_message",
        {
            "detail_type": "group",
            "group_id": GROUP_ID,
            "message": message,
        },
        {"message_id": message_id, "time": time},
    )
    await check_record(
        datetime.utcfromtimestamp(time),
        message_id,
        "group",
        message,
        bot.platform,
        send_msg=True,
        user_id=bot.self_id,
        group_id=GROUP_ID,
    )

    message_id = "11451455555"
    message = Message("test call_api send_message private message")
    await record_send_msg_v12(
        bot,
        None,
        "send_message",
        {
            "detail_type": "private",
            "message": message,
        },
        {"message_id": message_id, "time": time},
    )
    await check_record(
        datetime.utcfromtimestamp(time),
        message_id,
        "private",
        message,
        bot.platform,
        send_msg=True,
        user_id=bot.self_id,
    )

    message_id = "11451466666"
    message = Message("test call_api send_message channel message")
    await record_send_msg_v12(
        bot,
        None,
        "send_message",
        {
            "detail_type": "channel",
            "guild_id": GUILD_ID,
            "channel_id": CHANNEL_ID,
            "message": message,
        },
        {"message_id": message_id, "time": time},
    )
    await check_record(
        datetime.utcfromtimestamp(time),
        message_id,
        "channel",
        message,
        bot.platform,
        send_msg=True,
        user_id=bot.self_id,
        guild_id=GUILD_ID,
        channel_id=CHANNEL_ID,
    )


async def check_record(
    time: datetime,
    message_id: str,
    detail_type: str,
    message: "Message",
    platform: str,
    send_msg: bool = False,
    user_id: str = "",
    group_id: Optional[str] = None,
    guild_id: Optional[str] = None,
    channel_id: Optional[str] = None,
):
    from typing import List
    from sqlmodel import select

    from nonebot_plugin_chatrecorder import serialize_message
    from nonebot_plugin_chatrecorder.model import MessageRecord
    from nonebot_plugin_datastore import create_session

    statement = select(MessageRecord).where(MessageRecord.message_id == message_id)
    async with create_session() as session:
        records: List[MessageRecord] = (await session.exec(statement)).all()  # type: ignore

    assert len(records) == 1
    record = records[0]
    if send_msg:
        assert record.type == "message_sent"
    else:
        assert record.type == "message"
    assert record.detail_type == detail_type
    assert record.time == time
    assert record.platform == platform
    assert record.message == serialize_message(message)
    assert record.alt_message == message.extract_plain_text()
    assert record.user_id == user_id
    assert record.group_id == group_id
    assert record.guild_id == guild_id
    assert record.channel_id == channel_id
