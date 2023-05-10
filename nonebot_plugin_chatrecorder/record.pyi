from datetime import datetime
from typing import Iterable, List, Literal, Optional, Union

from nonebot.adapters import Bot, Message

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
    bot: Bot,
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
) -> List[Message]: ...
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
