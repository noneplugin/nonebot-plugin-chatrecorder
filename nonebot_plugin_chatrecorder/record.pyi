from collections.abc import Iterable
from datetime import datetime
from typing import Literal

from nonebot.adapters import Message
from nonebot_plugin_session import Session, SessionIdType, SessionLevel
from sqlalchemy.sql import ColumnElement

from .model import MessageRecord

def filter_statement(
    *,
    session: Session | None = None,
    id_type: SessionIdType = ...,
    include_platform: bool = True,
    include_bot_type: bool = True,
    include_bot_id: bool = True,
    bot_ids: Iterable[str] | None = None,
    bot_types: Iterable[str] | None = None,
    platforms: Iterable[str] | None = None,
    levels: Iterable[int | SessionLevel] | None = None,
    id1s: Iterable[str] | None = None,
    id2s: Iterable[str] | None = None,
    id3s: Iterable[str] | None = None,
    exclude_id1s: Iterable[str] | None = None,
    exclude_id2s: Iterable[str] | None = None,
    exclude_id3s: Iterable[str] | None = None,
    time_start: datetime | None = None,
    time_stop: datetime | None = None,
    types: Iterable[Literal["message", "message_sent"]] | None = None,
) -> list[ColumnElement[bool]]: ...
async def get_message_records(
    *,
    session: Session | None = None,
    id_type: SessionIdType = ...,
    include_platform: bool = True,
    include_bot_type: bool = True,
    include_bot_id: bool = True,
    bot_ids: Iterable[str] | None = None,
    bot_types: Iterable[str] | None = None,
    platforms: Iterable[str] | None = None,
    levels: Iterable[int | SessionLevel] | None = None,
    id1s: Iterable[str] | None = None,
    id2s: Iterable[str] | None = None,
    id3s: Iterable[str] | None = None,
    exclude_id1s: Iterable[str] | None = None,
    exclude_id2s: Iterable[str] | None = None,
    exclude_id3s: Iterable[str] | None = None,
    time_start: datetime | None = None,
    time_stop: datetime | None = None,
    types: Iterable[Literal["message", "message_sent"]] | None = None,
) -> list[MessageRecord]: ...
async def get_messages(
    *,
    session: Session | None = None,
    id_type: SessionIdType = ...,
    include_platform: bool = True,
    include_bot_type: bool = True,
    include_bot_id: bool = True,
    bot_ids: Iterable[str] | None = None,
    bot_types: Iterable[str] | None = None,
    platforms: Iterable[str] | None = None,
    levels: Iterable[int | SessionLevel] | None = None,
    id1s: Iterable[str] | None = None,
    id2s: Iterable[str] | None = None,
    id3s: Iterable[str] | None = None,
    exclude_id1s: Iterable[str] | None = None,
    exclude_id2s: Iterable[str] | None = None,
    exclude_id3s: Iterable[str] | None = None,
    time_start: datetime | None = None,
    time_stop: datetime | None = None,
    types: Iterable[Literal["message", "message_sent"]] | None = None,
) -> list[Message]: ...
async def get_messages_plain_text(
    *,
    session: Session | None = None,
    id_type: SessionIdType = ...,
    include_platform: bool = True,
    include_bot_type: bool = True,
    include_bot_id: bool = True,
    bot_ids: Iterable[str] | None = None,
    bot_types: Iterable[str] | None = None,
    platforms: Iterable[str] | None = None,
    levels: Iterable[int | SessionLevel] | None = None,
    id1s: Iterable[str] | None = None,
    id2s: Iterable[str] | None = None,
    id3s: Iterable[str] | None = None,
    exclude_id1s: Iterable[str] | None = None,
    exclude_id2s: Iterable[str] | None = None,
    exclude_id3s: Iterable[str] | None = None,
    time_start: datetime | None = None,
    time_stop: datetime | None = None,
    types: Iterable[Literal["message", "message_sent"]] | None = None,
) -> list[str]: ...
