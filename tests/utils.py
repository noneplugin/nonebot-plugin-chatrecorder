from datetime import datetime
from typing import Any, Dict, List, Optional


async def check_record(
    bot_id: str,
    bot_type: str,
    platform: str,
    level: str,
    id1: Optional[str],
    id2: Optional[str],
    id3: Optional[str],
    time: Optional[datetime],
    type: str,
    message_id: str,
    message: List[Dict[str, Any]],
    plain_text: str,
):
    from nonebot_plugin_datastore import create_session
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from nonebot_plugin_chatrecorder.model import MessageRecord
    from nonebot_plugin_chatrecorder.utils import remove_timezone

    statement = (
        select(MessageRecord)
        .where(MessageRecord.message_id == message_id)
        .options(selectinload(MessageRecord.session))
    )
    async with create_session() as db_session:
        records = (await db_session.scalars(statement)).all()

    assert len(records) == 1
    record = records[0]
    session = record.session
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
