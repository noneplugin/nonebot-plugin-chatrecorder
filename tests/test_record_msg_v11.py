import pytest
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from nonebot.adapters.onebot.v11 import Message

from nonebug.app import App

from .utils import fake_group_message_event_v11, fake_private_message_event_v11

USER_ID = 123456
GROUP_ID = 654321


@pytest.mark.asyncio
async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""

    from nonebot.adapters.onebot.v11 import Bot, Message
    from nonebot_plugin_chatrecorder import record_recv_msg_v11

    async with app.test_api() as ctx:
        bot = ctx.create_bot(base=Bot)

    time = 1000000

    message_id = 11451411111
    message = Message("test group message")
    event = fake_group_message_event_v11(
        time=time,
        user_id=USER_ID,
        group_id=GROUP_ID,
        message_id=message_id,
        message=message,
    )
    await record_recv_msg_v11(bot, event)
    await check_record(str(message_id), "message", "group", message, time=time)

    message_id = 11451422222
    message = Message("test private message")
    event = fake_private_message_event_v11(
        time=time, user_id=USER_ID, message_id=message_id, message=message
    )
    await record_recv_msg_v11(bot, event)
    await check_record(
        str(message_id), "message", "private", message, group_id=None, time=time
    )


@pytest.mark.asyncio
async def test_record_send_msg(app: App):
    """测试记录发送的消息"""

    from nonebot.adapters.onebot.v11 import Bot, Message
    from nonebot_plugin_chatrecorder import record_send_msg_v11

    async with app.test_api() as ctx:
        bot = ctx.create_bot(base=Bot)

    message_id = 11451433333
    message = Message("test call_api send_msg")
    await record_send_msg_v11(
        bot,
        None,
        "send_msg",
        {
            "message_type": "group",
            "group_id": GROUP_ID,
            "message": message,
        },
        {"message_id": message_id},
    )
    await check_record(
        str(message_id), "message_sent", "group", message, user_id=bot.self_id
    )

    message_id = 11451444444
    message = Message("test call_api send_group_msg")
    await record_send_msg_v11(
        bot,
        None,
        "send_group_msg",
        {
            "group_id": GROUP_ID,
            "message": message,
        },
        {"message_id": message_id},
    )
    await check_record(
        str(message_id), "message_sent", "group", message, user_id=bot.self_id
    )

    message_id = 11451455555
    message = Message("test call_api send_private_msg")
    await record_send_msg_v11(
        bot,
        None,
        "send_private_msg",
        {
            "user_id": USER_ID,
            "message": message,
        },
        {"message_id": message_id},
    )
    await check_record(
        str(message_id),
        "message_sent",
        "private",
        message,
        user_id=bot.self_id,
        group_id=None,
    )


async def check_record(
    message_id: str,
    type: str,
    detail_type: str,
    message: "Message",
    user_id: str = str(USER_ID),
    group_id: Optional[str] = str(GROUP_ID),
    time: Optional[int] = None,
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
    assert record.platform == "qq"
    assert record.type == type
    assert record.detail_type == detail_type
    assert record.message == serialize_message(message)
    assert record.plain_text == message.extract_plain_text()
    assert record.user_id == user_id
    assert record.group_id == group_id
    if time:
        assert record.time == datetime.utcfromtimestamp(time)
