from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from nonebot_plugin_uninfo import Session


def session_id(session: "Session") -> str:
    return f"{session.self_id}_{session.adapter}_{session.scope}_{session.id}"


async def check_record(
    session: "Session",
    time: Optional[datetime],
    type: str,
    message_id: str,
    message: list[dict[str, Any]],
    plain_text: str,
):
    from nonebot_plugin_orm import get_session
    from nonebot_plugin_uninfo.orm import get_session_model
    from sqlalchemy import select

    from nonebot_plugin_chatrecorder.model import MessageRecord
    from nonebot_plugin_chatrecorder.utils import remove_timezone

    statement = select(MessageRecord).where(MessageRecord.message_id == message_id)
    async with get_session() as db_session:
        records = (await db_session.scalars(statement)).all()

    assert len(records) == 1
    record = records[0]
    session_persist_id = record.session_persist_id
    session_model = await get_session_model(session_persist_id)
    record_session = await session_model.to_session()

    assert session_id(record_session) == session_id(session)
    assert record.type == type
    if time:
        assert record.time == remove_timezone(time)
    assert record.message == message
    assert record.plain_text == plain_text


async def assert_no_record(message_id: str):
    from nonebot_plugin_orm import get_session
    from sqlalchemy import select

    from nonebot_plugin_chatrecorder.model import MessageRecord

    statement = select(MessageRecord).where(MessageRecord.message_id == message_id)
    async with get_session() as db_session:
        records = (await db_session.scalars(statement)).all()

    assert len(records) == 0
