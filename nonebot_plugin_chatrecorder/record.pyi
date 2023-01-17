from datetime import datetime
from typing import Iterable, List, Literal, Optional, Union

from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v11 import Message as V11Msg

from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot.adapters.onebot.v12 import Message as V12Msg

from .model import MessageRecord

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
) -> List[MessageRecord]: ...
async def get_messages(
    bot: Union[V11Bot, V12Bot],
    *,
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
) -> Union[List[V11Msg], List[V12Msg]]: ...
async def get_messages_plain_text(
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
) -> List[str]: ...
