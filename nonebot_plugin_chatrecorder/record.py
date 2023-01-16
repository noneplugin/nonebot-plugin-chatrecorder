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
    bot: Union[V11Bot, V12Bot],
    *,
    user_ids: Optional[Iterable[str]] = None,
    group_ids: Optional[Iterable[str]] = None,
    guild_ids: Optional[Iterable[str]] = None,
    channel_ids: Optional[Iterable[str]] = None,
    exclude_user_ids: Optional[Iterable[str]] = None,
    exclude_group_ids: Optional[Iterable[str]] = None,
    exclude_guild_ids: Optional[Iterable[str]] = None,
    exclude_channel_ids: Optional[Iterable[str]] = None,
    types: Optional[Iterable[Literal["message", "message_sent"]]] = None,
    detail_types: Optional[Iterable[str]] = None,
    time_start: Optional[datetime] = None,
    time_stop: Optional[datetime] = None,
) -> List[MessageRecord]:
    """
    :说明:

      获取消息记录

    :参数:

      * ``bot: Union[V11Bot, V12Bot]``: Nonebot `Bot` 对象
      * ``user_ids: Optional[Iterable[str]]``: 用户列表，为空表示所有用户
      * ``group_ids: Optional[Iterable[str]]``: 群组列表，为空表示所有群组
      * ``guild_ids: Optional[Iterable[str]]``: 两级群组消息群组列表，为空表示所有群组
      * ``channel_ids: Optional[Iterable[str]]``: 两级群组消息频道列表，为空表示所有频道
      * ``exclude_user_ids: Optional[Iterable[str]]``: 不包含的用户列表，为空表示不限制
      * ``exclude_group_ids: Optional[Iterable[str]]``: 不包含的群组列表，为空表示不限制
      * ``exclude_guild_ids: Optional[Iterable[str]]``: 不包含的两级群组消息群组列表，为空表示不限制
      * ``exclude_channel_ids: Optional[Iterable[str]]``: 不包含的两级群组消息频道列表，为空表示不限制
      * ``types: Optional[Iterable[Literal["message", "message_sent"]]]``: 消息事件类型列表，为空表示所有类型
      * ``detail_types: Optional[List[str]]``: 消息事件具体类型列表，为空表示所有类型
      * ``time_start: Optional[datetime]``: 起始时间，UTC 时间，为空表示不限制起始时间
      * ``time_stop: Optional[datetime]``: 结束时间，UTC 时间，为空表示不限制结束时间

    :返回值:

      * ``List[MessageRecord]``: 消息记录列表
    """

    whereclause = []
    whereclause.append(MessageRecord.bot_id == bot.self_id)
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
    if types:
        for type in types:
            whereclause.append(MessageRecord.type == type)
    if detail_types:
        for detail_type in detail_types:
            whereclause.append(MessageRecord.detail_type == detail_type)
    if time_start:
        whereclause.append(MessageRecord.time >= time_start)
    if time_stop:
        whereclause.append(MessageRecord.time <= time_stop)

    statement = select(MessageRecord).where(*whereclause)
    async with create_session() as session:
        records: List[MessageRecord] = (await session.exec(statement)).all()  # type: ignore
    return records


@overload
async def get_messages(
    bot: V11Bot, *, plain_text: Literal[False], **kwargs
) -> List[V11Msg]:
    ...


@overload
async def get_messages(
    bot: V12Bot, *, plain_text: Literal[False], **kwargs
) -> List[V12Msg]:
    ...


@overload
async def get_messages(
    bot: Union[V11Bot, V12Bot], *, plain_text: Literal[True] = ..., **kwargs
) -> List[str]:
    ...


async def get_messages(
    bot: Union[V11Bot, V12Bot], *, plain_text: bool = False, **kwargs
) -> Union[List[str], List[V11Msg], List[V12Msg]]:
    """
    :说明:

      获取消息记录的消息列表

    :参数:

      * ``bot: Union[V11Bot, V12Bot]``: Nonebot `Bot` 对象
      * ``plain_text: bool = False``: 为 `True` 则返回字符串数组，否则返回 `Message` 数组
      * ``**kwargs``: 其他参数，具体查看 `get_message_records` 中的定义

    :返回值:

      * ``Union[List[str], List[V11Msg], List[V12Msg]]``: 消息列表
    """

    records: List[MessageRecord] = await get_message_records(bot, **kwargs)
    if plain_text:
        return [record.alt_message for record in records]
    else:
        if isinstance(bot, V11Bot):
            return [deserialize_message(record.message, V11Msg) for record in records]
        else:
            return [deserialize_message(record.message, V12Msg) for record in records]
