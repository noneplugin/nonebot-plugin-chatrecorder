from datetime import datetime
from typing import Iterable, List, Literal, Optional, Union

from nonebot.adapters import Message
from nonebot_plugin_session import Session, SessionIdType, SessionLevel
from sqlalchemy.sql import ColumnElement

from .model import MessageRecord

def filter_statement(
    *,
    session: Optional[Session] = None,
    id_type: SessionIdType = SessionIdType.GROUP_USER,
    include_platform: bool = True,
    include_bot_type: bool = True,
    include_bot_id: bool = True,
    bot_ids: Optional[Iterable[str]] = None,
    bot_types: Optional[Iterable[str]] = None,
    platforms: Optional[Iterable[str]] = None,
    levels: Optional[Iterable[Union[int, SessionLevel]]] = None,
    id1s: Optional[Iterable[str]] = None,
    id2s: Optional[Iterable[str]] = None,
    id3s: Optional[Iterable[str]] = None,
    exclude_id1s: Optional[Iterable[str]] = None,
    exclude_id2s: Optional[Iterable[str]] = None,
    exclude_id3s: Optional[Iterable[str]] = None,
    time_start: Optional[datetime] = None,
    time_stop: Optional[datetime] = None,
    types: Optional[Iterable[Literal["message", "message_sent"]]] = None,
) -> List[ColumnElement[bool]]: ...
async def get_message_records(
    *,
    session: Optional[Session] = None,
    id_type: SessionIdType = SessionIdType.GROUP_USER,
    include_platform: bool = True,
    include_bot_type: bool = True,
    include_bot_id: bool = True,
    bot_ids: Optional[Iterable[str]] = None,
    bot_types: Optional[Iterable[str]] = None,
    platforms: Optional[Iterable[str]] = None,
    levels: Optional[Iterable[Union[int, SessionLevel]]] = None,
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
    *,
    session: Optional[Session] = None,
    id_type: SessionIdType = SessionIdType.GROUP_USER,
    include_platform: bool = True,
    include_bot_type: bool = True,
    include_bot_id: bool = True,
    bot_ids: Optional[Iterable[str]] = None,
    bot_types: Optional[Iterable[str]] = None,
    platforms: Optional[Iterable[str]] = None,
    levels: Optional[Iterable[Union[int, SessionLevel]]] = None,
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
    session: Optional[Session] = None,
    id_type: SessionIdType = SessionIdType.GROUP_USER,
    include_platform: bool = True,
    include_bot_type: bool = True,
    include_bot_id: bool = True,
    bot_ids: Optional[Iterable[str]] = None,
    bot_types: Optional[Iterable[str]] = None,
    platforms: Optional[Iterable[str]] = None,
    levels: Optional[Iterable[Union[int, SessionLevel]]] = None,
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
