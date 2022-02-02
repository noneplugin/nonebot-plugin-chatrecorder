import pytest
from nonebug import App

from .utils import fake_group_message_event, fake_private_message_event


USER_ID = 123456
GROUP_ID = 654321


@pytest.mark.asyncio
async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""

    from nonebot_plugin_chatrecorder import record_recv_msg
    from nonebot.adapters.onebot.v11 import Message

    async with app.test_api() as ctx:
        bot = ctx.create_bot()

    message_id = 11451411111
    message = "test group message"
    event = fake_group_message_event(
        user_id=USER_ID,
        group_id=GROUP_ID,
        message_id=message_id,
        message=Message(message),
    )
    await record_recv_msg(event)
    await check_record(str(message_id), "group", message)

    message_id = 11451422222
    message = "test private message"
    event = fake_private_message_event(
        user_id=USER_ID,
        message_id=message_id,
        message=Message(message),
    )
    await record_recv_msg(event)
    await check_record(str(message_id), "private", message, group_id="")


@pytest.mark.asyncio
async def test_record_send_msg(app: App):
    """测试记录发送的消息"""

    from nonebot_plugin_chatrecorder import record_send_msg

    async with app.test_api() as ctx:
        bot = ctx.create_bot()

    message_id = 11451433333
    message = "test call_api send_msg"
    await record_send_msg(
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
    await check_record(str(message_id), "group", message, user_id=bot.self_id)

    message_id = 11451444444
    message = "test call_api send_group_msg"
    await record_send_msg(
        bot,
        None,
        "send_group_msg",
        {
            "group_id": GROUP_ID,
            "message": message,
        },
        {"message_id": message_id},
    )
    await check_record(str(message_id), "group", message, user_id=bot.self_id)

    message_id = 11451455555
    message = "test call_api send_private_msg"
    await record_send_msg(
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
        str(message_id), "private", message, user_id=bot.self_id, group_id=""
    )


async def check_record(
    message_id: str,
    message_type: str,
    message: str,
    user_id=str(USER_ID),
    group_id=str(GROUP_ID),
):
    from typing import List
    from sqlmodel import select

    from nonebot_plugin_chatrecorder import serialize_message
    from nonebot_plugin_chatrecorder.model import MessageRecord
    from nonebot_plugin_datastore import create_session
    from nonebot.adapters.onebot.v11 import Message

    statement = select(MessageRecord).where(MessageRecord.message_id == message_id)
    async with create_session() as session:
        records: List[MessageRecord] = (await session.exec(statement)).all()

    assert len(records) == 1
    record = records[0]
    assert record.platform == "qq"
    assert record.type == "message"
    assert record.detail_type == message_type
    assert record.message == serialize_message(Message(message))
    assert record.alt_message == message
    assert record.user_id == user_id
    assert record.group_id == group_id
