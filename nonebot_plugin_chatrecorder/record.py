from datetime import datetime
from sqlmodel import or_, select
from typing import Iterable, List, Literal, Optional, Union, overload

from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v11 import Message as V11Msg

from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot.adapters.onebot.v12 import Message as V12Msg

from nonebot_plugin_datastore import create_session

from .model import MessageRecord
from .message import deserialize_message


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
) -> List[MessageRecord]:
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
            or_(*[MessageRecord.bot_type == bot_type for bot_type in bot_types])  # type: ignore
        )
    if bot_ids:
        whereclause.append(
            or_(*[MessageRecord.bot_id == bot_id for bot_id in bot_ids])  # type: ignore
        )
    if platforms:
        whereclause.append(
            or_(*[MessageRecord.platform == platform for platform in platforms])  # type: ignore
        )
    if time_start:
        whereclause.append(MessageRecord.time >= time_start)
    if time_stop:
        whereclause.append(MessageRecord.time <= time_stop)
    if types:
        whereclause.append(
            or_(*[MessageRecord.type == type for type in types])  # type: ignore
        )
    if detail_types:
        whereclause.append(
            or_(*[MessageRecord.detail_type == detail_type for detail_type in detail_types])  # type: ignore
        )
    if user_ids:
        whereclause.append(
            or_(*[MessageRecord.user_id == user_id for user_id in user_ids])  # type: ignore
        )
    if group_ids:
        whereclause.append(
            or_(*[MessageRecord.group_id == group_id for group_id in group_ids])  # type: ignore
        )
    if guild_ids:
        whereclause.append(
            or_(*[MessageRecord.guild_id == guild_id for guild_id in guild_ids])  # type: ignore
        )
    if channel_ids:
        whereclause.append(
            or_(*[MessageRecord.channel_id == channel_id for channel_id in channel_ids])  # type: ignore
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
        records: List[MessageRecord] = (await session.exec(statement)).all()  # type: ignore
    return records


@overload
async def get_messages(bot: V11Bot, **kwargs) -> List[V11Msg]:
    ...


@overload
async def get_messages(bot: V12Bot, **kwargs) -> List[V12Msg]:
    ...


async def get_messages(
    bot: Union[V11Bot, V12Bot], **kwargs
) -> Union[List[V11Msg], List[V12Msg]]:
    """获取消息记录的消息列表

    参数:
      * ``bot: Union[V11Bot, V12Bot]``: Nonebot `Bot` 对象，用于判断消息类型
      * ``**kwargs``: 筛选参数，具体查看 `get_message_records` 中的定义

    返回值:
      * ``Union[List[V11Msg], List[V12Msg]]``: 消息列表
    """
    kwargs.update({"bot_types": [bot.adapter.get_name()]})
    records: List[MessageRecord] = await get_message_records(**kwargs)
    if isinstance(bot, V11Bot):
        return [deserialize_message(record.message, V11Msg) for record in records]
    else:
        return [deserialize_message(record.message, V12Msg) for record in records]


async def get_messages_plain_text(**kwargs) -> List[str]:
    """获取消息记录的纯文本消息列表

    参数:
      * ``**kwargs``: 筛选参数，具体查看 `get_message_records` 中的定义

    返回值:
      * ``List[str]``: 纯文本消息列表
    """
    records: List[MessageRecord] = await get_message_records(**kwargs)
    return [record.plain_text for record in records]
