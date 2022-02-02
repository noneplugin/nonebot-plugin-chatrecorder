import pytest
from nonebug.app import App
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nonebot_plugin_chatrecorder.model import MessageRecord


@pytest.mark.asyncio
async def test_get_message_records(app: App):
    """测试获取消息记录"""

    from typing import List
    from datetime import datetime

    from nonebot_plugin_chatrecorder import get_message_records
    from nonebot.adapters.onebot.v11 import Message

    async with app.test_api() as ctx:
        bot = ctx.create_bot()

    records = [
        make_record(
            "11451466666",
            "test message 1",
            "111111",
            "999999",
            datetime(2000, 1, 1, 0, 0, 0),
        ),
        make_record(
            "11451477777",
            "test message 2",
            "222222",
            "999999",
            datetime(2000, 1, 1, 1, 0, 0),
        ),
        make_record(
            "11451488888",
            "test message 3",
            "222222",
            "888888",
            datetime(2000, 1, 1, 2, 0, 0),
        ),
        make_record(
            "11451499999",
            "test message 4",
            "222222",
            "",
            datetime(2000, 1, 1, 3, 0, 0),
            message_type="private",
        ),
    ]
    for record in records:
        await add_record(record)

    msgs = await get_message_records(user_ids=["222222"])
    assert len(msgs) == 3
    assert isinstance(msgs[0], Message)
    msgs = await get_message_records(user_ids=["222222"], plain_text=False)
    assert isinstance(msgs[0], Message)
    msgs = await get_message_records(user_ids=["222222"], plain_text=True)
    assert isinstance(msgs[0], str)
    msgs = await get_message_records(group_ids=["999999"])
    assert len(msgs) == 2
    msgs = await get_message_records(user_ids=["222222"], group_ids=["999999"])
    assert len(msgs) == 1
    msgs = await get_message_records(user_ids=["222222"], message_type="group")
    assert len(msgs) == 2
    msgs = await get_message_records(
        time_start=datetime(2000, 1, 1, 0, 0, 0),
        time_stop=datetime(2000, 1, 1, 3, 0, 0),
    )
    assert len(msgs) == 4


def make_record(
    message_id: str,
    message: str,
    user_id: str,
    group_id: str,
    time: datetime,
    message_type: str = "group",
):
    from nonebot_plugin_chatrecorder import serialize_message
    from nonebot_plugin_chatrecorder.model import MessageRecord
    from nonebot.adapters.onebot.v11 import Message

    return MessageRecord(
        platform="qq",
        time=time,
        type="message",
        detail_type=message_type,
        message_id=str(message_id),
        message=serialize_message(Message(message)),
        alt_message=message,
        user_id=user_id,
        group_id=group_id,
    )


async def add_record(record: "MessageRecord"):
    from nonebot_plugin_datastore import create_session

    async with create_session() as session:
        session.add(record)
        await session.commit()
