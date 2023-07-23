from datetime import datetime, timezone
from typing import Iterable, List, Literal, Optional, Sequence, Union

from nonebot.adapters import Bot, Message
from nonebot_plugin_datastore import create_session
from nonebot_plugin_session import SessionLevel
from nonebot_plugin_session.model import SessionModel
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from .message import deserialize_message
from .model import MessageRecord


def remove_timezone(dt: datetime) -> datetime:
    """移除时区"""
    if dt.tzinfo is None:
        return dt
    # 先转至 UTC 时间，再移除时区
    dt = dt.astimezone(timezone.utc)
    return dt.replace(tzinfo=None)


async def get_message_records(
    *,
    bot_ids: Optional[Iterable[str]] = None,
    bot_types: Optional[Iterable[str]] = None,
    platforms: Optional[Iterable[str]] = None,
    levels: Optional[Iterable[Union[str, SessionLevel]]] = None,
    id1s: Optional[Iterable[str]] = None,
    id2s: Optional[Iterable[str]] = None,
    id3s: Optional[Iterable[str]] = None,
    exclude_id1s: Optional[Iterable[str]] = None,
    exclude_id2s: Optional[Iterable[str]] = None,
    exclude_id3s: Optional[Iterable[str]] = None,
    time_start: Optional[datetime] = None,
    time_stop: Optional[datetime] = None,
    types: Optional[Iterable[Literal["message", "message_sent"]]] = None,
) -> Sequence[MessageRecord]:
    """获取消息记录

    参数:
      * ``bot_ids: Optional[Iterable[str]]``: bot id 列表，为空表示所有 bot id
      * ``bot_types: Optional[Iterable[str]]``: 协议适配器类型列表，为空表示所有适配器
      * ``platforms: Optional[Iterable[str]]``: 平台类型列表，为空表示所有平台
      * ``levels: Optional[Iterable[Union[str, SessionLevel]]]``: 会话级别列表，为空表示所有级别
      * ``id1s: Optional[Iterable[str]]``: 会话 id1（用户级 id）列表，为空表示所有 id
      * ``id2s: Optional[Iterable[str]]``: 会话 id2（群组级 id）列表，为空表示所有 id
      * ``id3s: Optional[Iterable[str]]``: 会话 id3（两级群组级 id）列表，为空表示所有 id
      * ``exclude_id1s: Optional[Iterable[str]]``: 不包含的会话 id1（用户级 id）列表，为空表示不限制
      * ``exclude_id2s: Optional[Iterable[str]]``: 不包含的会话 id2（群组级 id）列表，为空表示不限制
      * ``exclude_id3s: Optional[Iterable[str]]``: 不包含的会话 id3（两级群组级 id）列表，为空表示不限制
      * ``time_start: Optional[datetime]``: 起始时间，UTC 时间，为空表示不限制起始时间
      * ``time_stop: Optional[datetime]``: 结束时间，UTC 时间，为空表示不限制结束时间
      * ``types: Optional[Iterable[Literal["message", "message_sent"]]]``: 消息事件类型列表，为空表示所有类型

    返回值:
      * ``List[MessageRecord]``: 消息记录列表
    """

    whereclause = []

    if bot_types:
        whereclause.append(
            or_(*[SessionModel.bot_type == bot_type for bot_type in bot_types])
        )
    if bot_ids:
        whereclause.append(or_(*[SessionModel.bot_id == bot_id for bot_id in bot_ids]))
    if platforms:
        whereclause.append(
            or_(*[SessionModel.platform == platform for platform in platforms])
        )
    if levels:
        whereclause.append(or_(*[SessionModel.level == level for level in levels]))
    if id1s:
        whereclause.append(or_(*[SessionModel.id1 == id1 for id1 in id1s]))
    if id2s:
        whereclause.append(or_(*[SessionModel.id2 == id2 for id2 in id2s]))
    if id3s:
        whereclause.append(or_(*[SessionModel.id3 == id3 for id3 in id3s]))
    if exclude_id1s:
        for id1 in exclude_id1s:
            whereclause.append(SessionModel.id1 != id1)
    if exclude_id2s:
        for id2 in exclude_id2s:
            whereclause.append(SessionModel.id2 != id2)
    if exclude_id3s:
        for id3 in exclude_id3s:
            whereclause.append(SessionModel.id3 != id3)
    if time_start:
        whereclause.append(MessageRecord.time >= remove_timezone(time_start))
    if time_stop:
        whereclause.append(MessageRecord.time <= remove_timezone(time_stop))
    if types:
        whereclause.append(or_(*[MessageRecord.type == type for type in types]))

    statement = (
        select(MessageRecord)
        .where(*whereclause)
        .join(SessionModel)
        .options(selectinload(MessageRecord.session))
    )
    async with create_session() as db_session:
        records = (await db_session.scalars(statement)).all()
    return records


async def get_messages(bot: Bot, **kwargs) -> List[Message]:
    """获取消息记录的消息列表

    参数:
      * ``bot: Bot``: Nonebot `Bot` 对象，用于判断消息类型
      * ``**kwargs``: 筛选参数，具体查看 `get_message_records` 中的定义

    返回值:
      * ``List[Message]``: 消息列表
    """
    bot_type = bot.type
    kwargs.update({"bot_types": [bot_type]})
    records = await get_message_records(**kwargs)
    return [deserialize_message(bot, record.message) for record in records]


async def get_messages_plain_text(**kwargs) -> List[str]:
    """获取消息记录的纯文本消息列表

    参数:
      * ``**kwargs``: 筛选参数，具体查看 `get_message_records` 中的定义

    返回值:
      * ``List[str]``: 纯文本消息列表
    """
    records = await get_message_records(**kwargs)
    return [record.plain_text for record in records]
