from datetime import datetime, timezone
from typing import Iterable, List, Literal, Optional, Sequence

from nonebot.adapters import Bot, Message
from nonebot_plugin_datastore import create_session
from sqlalchemy import or_, select

from .adapters import get_message_class_by_adapter_name
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
    bot_types: Optional[Iterable[str]] = None,
    bot_ids: Optional[Iterable[str]] = None,
    platforms: Optional[Iterable[str]] = None,
    time_start: Optional[datetime] = None,
    time_stop: Optional[datetime] = None,
    types: Optional[Iterable[Literal["message", "message_sent"]]] = None,
    detail_types: Optional[Iterable[str]] = None,
    user_ids: Optional[Iterable[str]] = None,
    group_ids: Optional[Iterable[str]] = None,
    guild_ids: Optional[Iterable[str]] = None,
    channel_ids: Optional[Iterable[str]] = None,
    exclude_user_ids: Optional[Iterable[str]] = None,
    exclude_group_ids: Optional[Iterable[str]] = None,
    exclude_guild_ids: Optional[Iterable[str]] = None,
    exclude_channel_ids: Optional[Iterable[str]] = None,
) -> Sequence[MessageRecord]:
    """获取消息记录

    参数:
      * ``bot_types: Optional[Iterable[str]]``: 协议适配器类型列表，为空表示所有适配器
      * ``bot_ids: Optional[Iterable[str]]``: bot id 列表，为空表示所有 bot id
      * ``platforms: Optional[Iterable[str]]``: 平台类型列表，为空表示所有平台
      * ``time_start: Optional[datetime]``: 起始时间，UTC 时间，为空表示不限制起始时间
      * ``time_stop: Optional[datetime]``: 结束时间，UTC 时间，为空表示不限制结束时间
      * ``types: Optional[Iterable[Literal["message", "message_sent"]]]``: 消息事件类型列表，为空表示所有类型
      * ``detail_types: Optional[List[str]]``: 消息事件具体类型列表，为空表示所有类型
      * ``user_ids: Optional[Iterable[str]]``: 用户列表，为空表示所有用户
      * ``group_ids: Optional[Iterable[str]]``: 群组列表，为空表示所有群组
      * ``guild_ids: Optional[Iterable[str]]``: 两级群组消息群组列表，为空表示所有群组
      * ``channel_ids: Optional[Iterable[str]]``: 两级群组消息频道列表，为空表示所有频道
      * ``exclude_user_ids: Optional[Iterable[str]]``: 不包含的用户列表，为空表示不限制
      * ``exclude_group_ids: Optional[Iterable[str]]``: 不包含的群组列表，为空表示不限制
      * ``exclude_guild_ids: Optional[Iterable[str]]``: 不包含的两级群组消息群组列表，为空表示不限制
      * ``exclude_channel_ids: Optional[Iterable[str]]``: 不包含的两级群组消息频道列表，为空表示不限制

    返回值:
      * ``List[MessageRecord]``: 消息记录列表
    """

    whereclause = []

    if bot_types:
        whereclause.append(
            or_(*[MessageRecord.bot_type == bot_type for bot_type in bot_types])
        )
    if bot_ids:
        whereclause.append(or_(*[MessageRecord.bot_id == bot_id for bot_id in bot_ids]))
    if platforms:
        whereclause.append(
            or_(*[MessageRecord.platform == platform for platform in platforms])
        )
    if time_start:
        whereclause.append(MessageRecord.time >= remove_timezone(time_start))
    if time_stop:
        whereclause.append(MessageRecord.time <= remove_timezone(time_stop))
    if types:
        whereclause.append(or_(*[MessageRecord.type == type for type in types]))
    if detail_types:
        whereclause.append(
            or_(
                *[
                    MessageRecord.detail_type == detail_type
                    for detail_type in detail_types
                ]
            )
        )
    if user_ids:
        whereclause.append(
            or_(*[MessageRecord.user_id == user_id for user_id in user_ids])
        )
    if group_ids:
        whereclause.append(
            or_(*[MessageRecord.group_id == group_id for group_id in group_ids])
        )
    if guild_ids:
        whereclause.append(
            or_(*[MessageRecord.guild_id == guild_id for guild_id in guild_ids])
        )
    if channel_ids:
        whereclause.append(
            or_(*[MessageRecord.channel_id == channel_id for channel_id in channel_ids])
        )
    if exclude_user_ids:
        for user_id in exclude_user_ids:
            whereclause.append(MessageRecord.user_id != user_id)
    if exclude_group_ids:
        for group_id in exclude_group_ids:
            whereclause.append(MessageRecord.group_id != group_id)
    if exclude_guild_ids:
        for guild_id in exclude_guild_ids:
            whereclause.append(MessageRecord.guild_id != guild_id)
    if exclude_channel_ids:
        for channel_id in exclude_channel_ids:
            whereclause.append(MessageRecord.channel_id != channel_id)

    statement = select(MessageRecord).where(*whereclause)
    async with create_session() as session:
        records = (await session.scalars(statement)).all()
    return records


async def get_messages(bot: Bot, **kwargs) -> List[Message]:
    """获取消息记录的消息列表

    参数:
      * ``bot: Bot``: Nonebot `Bot` 对象，用于判断消息类型
      * ``**kwargs``: 筛选参数，具体查看 `get_message_records` 中的定义

    返回值:
      * ``List[Message]``: 消息列表
    """
    adapter_name = bot.adapter.get_name()
    msg_class = get_message_class_by_adapter_name(adapter_name)
    kwargs.update({"bot_types": [adapter_name]})
    records = await get_message_records(**kwargs)
    return [deserialize_message(record.message, msg_class) for record in records]


async def get_messages_plain_text(**kwargs) -> List[str]:
    """获取消息记录的纯文本消息列表

    参数:
      * ``**kwargs``: 筛选参数，具体查看 `get_message_records` 中的定义

    返回值:
      * ``List[str]``: 纯文本消息列表
    """
    records = await get_message_records(**kwargs)
    return [record.plain_text for record in records]
