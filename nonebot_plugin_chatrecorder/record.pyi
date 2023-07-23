from datetime import datetime
from typing import Iterable, List, Literal, Optional, Union

from nonebot.adapters import Bot, Message
from nonebot_plugin_session import SessionLevel

from .model import MessageRecord

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
) -> List[MessageRecord]: ...
async def get_messages(
    bot: Bot,
    *,
    bot_ids: Optional[Iterable[str]] = None,
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
) -> List[Message]: ...
async def get_messages_plain_text(
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
) -> List[str]: ...
