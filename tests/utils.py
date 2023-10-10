from datetime import datetime
from typing import Any, Dict, List, Optional


async def check_record(
    bot_id: str,
    bot_type: str,
    platform: str,
    level: int,
    id1: Optional[str],
    id2: Optional[str],
    id3: Optional[str],
    time: Optional[datetime],
    type: str,
    message_id: str,
    message: List[Dict[str, Any]],
    plain_text: str,
):
    from nonebot_plugin_orm import get_session
    from nonebot_plugin_session_orm import get_session_by_persist_id
    from sqlalchemy import select

    from nonebot_plugin_chatrecorder.model import MessageRecord
    from nonebot_plugin_chatrecorder.utils import remove_timezone

    statement = select(MessageRecord).where(MessageRecord.message_id == message_id)
    async with get_session() as db_session:
        records = (await db_session.scalars(statement)).all()

    assert len(records) == 1
    record = records[0]
    session_persist_id = record.session_persist_id
    session = await get_session_by_persist_id(session_persist_id)
    assert session.bot_id == bot_id
    assert session.bot_type == bot_type
    assert session.platform == platform
    assert session.level == level
    assert session.id1 == id1
    assert session.id2 == id2
    assert session.id3 == id3
    assert record.type == type
    if time:
        assert record.time == remove_timezone(time)
    assert record.message == message
    assert record.plain_text == plain_text
