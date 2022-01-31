from sqlmodel import select
from typing import Iterable, List, Optional, Literal

from nonebot.adapters.onebot.v11 import Message

from .model import MessageRecord, session
from .message import deserialize_message


async def get_message_records(
    user_ids: Optional[Iterable[str]] = None,
    group_ids: Optional[Iterable[str]] = None,
    exclude_user_ids: Optional[Iterable[str]] = None,
    exclude_group_ids: Optional[Iterable[str]] = None,
    message_type: Optional[Literal['private', 'group']] = None,
    time_start: Optional[int] = None,
    time_stop: Optional[int] = None,
) -> List[Message]:
    """
    :说明:

      获取消息记录

    :参数:

      * ``user_ids: Optional[Iterable[str]]``: 用户列表，为空表示所有用户
      * ``group_ids: Optional[Iterable[str]]``: 群组列表，为空表示所有群组
      * ``exclude_user_ids: Optional[Iterable[str]]``: 不包含的用户列表，为空表示不限制
      * ``exclude_group_ids: Optional[Iterable[str]]``: 不包含的群组列表，为空表示不限制
      * ``message_type: Optional[Literal['private', 'group']]``: 消息类型，可选值：'private' 和 'group'，为空表示所有类型
      * ``time_start: Optional[int]``: 起始时间，类型为时间戳，单位为秒，为空表示不限制起始时间
      * ``time_stop: Optional[int]``: 结束时间，类型为时间戳，单位为秒，为空表示不限制结束时间

    :返回值:

      * ``List[Message]``: 消息列表
    """

    whereclause = []
    if user_ids:
        whereclause.append(MessageRecord.user_id in set(user_ids))
    if group_ids:
        whereclause.append(MessageRecord.group_id in set(group_ids))
    if exclude_user_ids:
        whereclause.append(MessageRecord.user_id not in set(exclude_user_ids))
    if exclude_group_ids:
        whereclause.append(MessageRecord.group_id not in set(exclude_group_ids))
    if message_type:
        whereclause.append(MessageRecord.detail_type == message_type)
    if time_start:
        whereclause.append(MessageRecord.time >= time_start)
    if time_stop:
        whereclause.append(MessageRecord.time <= time_stop)

    statement = select(MessageRecord).where(whereclause)
    records: List[MessageRecord] = (await session.exec(statement)).all()
    return [deserialize_message(record.message) for record in records]
