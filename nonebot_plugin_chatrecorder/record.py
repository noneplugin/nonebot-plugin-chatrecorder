from collections.abc import Iterable, Sequence
from datetime import datetime
from typing import Literal, Optional, Union

from nonebot.adapters import Message
from nonebot_plugin_orm import get_session
from nonebot_plugin_uninfo import SceneType, Session, SupportAdapter, SupportScope
from nonebot_plugin_uninfo.orm import BotModel, SceneModel, SessionModel, UserModel
from sqlalchemy import or_, select
from sqlalchemy.sql import ColumnElement

from .message import deserialize_message
from .model import MessageRecord
from .utils import adapter_value, remove_timezone, scene_type_value, scope_value


def filter_statement(
    *,
    session: Optional[Session] = None,
    filter_self_id: bool = True,
    filter_adapter: bool = True,
    filter_scope: bool = True,
    filter_scene: bool = True,
    filter_user: bool = True,
    self_ids: Optional[Iterable[str]] = None,
    adapters: Optional[Iterable[Union[str, SupportAdapter]]] = None,
    scopes: Optional[Iterable[Union[str, SupportScope]]] = None,
    scene_types: Optional[Iterable[Union[int, SceneType]]] = None,
    scene_ids: Optional[Iterable[str]] = None,
    user_ids: Optional[Iterable[str]] = None,
    exclude_self_ids: Optional[Iterable[str]] = None,
    exclude_adapters: Optional[Iterable[Union[str, SupportAdapter]]] = None,
    exclude_scopes: Optional[Iterable[Union[str, SupportScope]]] = None,
    exclude_scene_types: Optional[Iterable[Union[int, SceneType]]] = None,
    exclude_scene_ids: Optional[Iterable[str]] = None,
    exclude_user_ids: Optional[Iterable[str]] = None,
    time_start: Optional[datetime] = None,
    time_stop: Optional[datetime] = None,
    types: Optional[Iterable[Literal["message", "message_sent"]]] = None,
) -> list[ColumnElement[bool]]:
    """筛选消息记录

    参数:
      * ``session: Optional[Session]``: 会话模型，传入时会根据 `session` 中的字段筛选
      * ``id_type: SessionIdType``: 会话 id 类型，仅在传入 `session` 时有效
      * ``filter_self_id: bool``: 是否筛选 bot id，仅在传入 `session` 时有效
      * ``filter_adapter: bool``: 是否筛选适配器类型，仅在传入 `session` 时有效
      * ``filter_scope: bool``: 是否筛选平台类型，仅在传入 `session` 时有效
      * ``filter_scene: bool``: 是否筛选事件场景，仅在传入 `session` 时有效
      * ``filter_user: bool``: 是否筛选用户，仅在传入 `session` 时有效
      * ``self_ids: Optional[Iterable[str]]``: bot id 列表，为空表示所有 bot id
      * ``adapters: Optional[Iterable[Union[str, SupportAdapter]]]``: 适配器类型列表，为空表示所有适配器
      * ``scopes: Optional[Iterable[Union[str, SupportScope]]]``: 平台类型列表，为空表示所有平台
      * ``scene_types: Optional[Iterable[Union[str, SceneType]]]``: 事件场景类型列表，为空表示所有类型
      * ``scene_ids: Optional[Iterable[str]]``: 事件场景 id 列表，为空表示所有 id
      * ``user_ids: Optional[Iterable[str]]``: 用户 id 列表，为空表示所有 id
      * ``exclude_self_ids: Optional[Iterable[str]]``: 不包含的 bot id 列表，为空表示不限制
      * ``exclude_adapters: Optional[Iterable[Union[str, SupportAdapter]]]``: 不包含的适配器类型列表，为空表示不限制
      * ``exclude_scopes: Optional[Iterable[Union[str, SupportScope]]]``: 不包含的平台类型列表，为空表示不限制
      * ``exclude_scene_types: Optional[Iterable[Union[str, SceneType]]]``: 不包含的事件场景类型列表，为空表示不限制
      * ``exclude_scene_ids: Optional[Iterable[str]]``: 不包含的事件场景 id 列表，为空表示不限制
      * ``exclude_user_ids: Optional[Iterable[str]]``: 不包含的用户 id 列表，为空表示不限制
      * ``time_start: Optional[datetime]``: 起始时间，为空表示不限制起始时间（传入带时区的时间或 UTC 时间）
      * ``time_stop: Optional[datetime]``: 结束时间，为空表示不限制结束时间（传入带时区的时间或 UTC 时间）
      * ``types: Optional[Iterable[Literal["message", "message_sent"]]]``: 消息事件类型列表，为空表示所有类型

    返回值:
      * ``List[ColumnElement[bool]]``: 筛选语句
    """

    whereclause: list[ColumnElement[bool]] = []
    if session:
        if filter_self_id:
            whereclause.append(BotModel.self_id == session.self_id)
        if filter_adapter:
            whereclause.append(BotModel.adapter == adapter_value(session.adapter))
        if filter_scope:
            whereclause.append(BotModel.scope == scope_value(session.scope))
        if filter_scene:
            whereclause.append(SceneModel.scene_id == session.scene.id)
            whereclause.append(SceneModel.scene_type == session.scene.type.value)
        if filter_user:
            whereclause.append(UserModel.user_id == session.user.id)

    if self_ids:
        whereclause.append(or_(*[BotModel.self_id == self_id for self_id in self_ids]))
    if adapters:
        whereclause.append(
            or_(*[BotModel.adapter == adapter_value(adapter) for adapter in adapters])
        )
    if scopes:
        whereclause.append(
            or_(*[BotModel.scope == scope_value(scope) for scope in scopes])
        )
    if scene_types:
        whereclause.append(
            or_(
                *[
                    SceneModel.scene_type == scene_type_value(scene_type)
                    for scene_type in scene_types
                ]
            )
        )
    if scene_ids:
        whereclause.append(
            or_(*[SceneModel.scene_id == scene_id for scene_id in scene_ids])
        )
    if user_ids:
        whereclause.append(or_(*[UserModel.user_id == user_id for user_id in user_ids]))
    if exclude_self_ids:
        for self_id in exclude_self_ids:
            whereclause.append(BotModel.self_id != self_id)
    if exclude_adapters:
        for adapter in exclude_adapters:
            whereclause.append(BotModel.adapter != adapter_value(adapter))
    if exclude_scopes:
        for scope in exclude_scopes:
            whereclause.append(BotModel.scope != scope_value(scope))
    if exclude_scene_types:
        for scene_type in exclude_scene_types:
            whereclause.append(SceneModel.scene_type != scene_type_value(scene_type))
    if exclude_scene_ids:
        for scene_id in exclude_scene_ids:
            whereclause.append(SceneModel.scene_id != scene_id)
    if exclude_user_ids:
        for user_id in exclude_user_ids:
            whereclause.append(UserModel.user_id != user_id)
    if time_start:
        whereclause.append(MessageRecord.time >= remove_timezone(time_start))
    if time_stop:
        whereclause.append(MessageRecord.time <= remove_timezone(time_stop))
    if types:
        whereclause.append(or_(*[MessageRecord.type == type for type in types]))
    return whereclause


async def get_message_records(**kwargs) -> Sequence[MessageRecord]:
    """获取消息记录

    参数:
      * ``**kwargs``: 筛选参数，具体查看 `filter_statement` 中的定义

    返回值:
      * ``List[MessageRecord]``: 消息记录列表
    """
    whereclause = filter_statement(**kwargs)
    statement = (
        select(MessageRecord)
        .where(*whereclause)
        .join(SessionModel, SessionModel.id == MessageRecord.session_persist_id)
        .join(BotModel, BotModel.id == SessionModel.bot_persist_id)
        .join(SceneModel, SceneModel.id == SessionModel.scene_persist_id)
        .join(UserModel, UserModel.id == SessionModel.user_persist_id)
    )
    async with get_session() as db_session:
        records = (await db_session.scalars(statement)).all()
    return records


async def get_messages(**kwargs) -> list[Message]:
    """获取消息记录的消息列表

    参数:
      * ``**kwargs``: 筛选参数，具体查看 `filter_statement` 中的定义

    返回值:
      * ``List[Message]``: 消息列表
    """
    whereclause = filter_statement(**kwargs)
    statement = (
        select(MessageRecord.message, BotModel.adapter)
        .where(*whereclause)
        .join(SessionModel, SessionModel.id == MessageRecord.session_persist_id)
        .join(BotModel, BotModel.id == SessionModel.bot_persist_id)
        .join(SceneModel, SceneModel.id == SessionModel.scene_persist_id)
        .join(UserModel, UserModel.id == SessionModel.user_persist_id)
    )
    async with get_session() as db_session:
        results = (await db_session.execute(statement)).all()
    return [deserialize_message(result[1], result[0]) for result in results]


async def get_messages_plain_text(**kwargs) -> Sequence[str]:
    """获取消息记录的纯文本消息列表

    参数:
      * ``**kwargs``: 筛选参数，具体查看 `filter_statement` 中的定义

    返回值:
      * ``List[str]``: 纯文本消息列表
    """
    whereclause = filter_statement(**kwargs)
    statement = (
        select(MessageRecord.plain_text)
        .where(*whereclause)
        .join(SessionModel, SessionModel.id == MessageRecord.session_persist_id)
        .join(BotModel, BotModel.id == SessionModel.bot_persist_id)
        .join(SceneModel, SceneModel.id == SessionModel.scene_persist_id)
        .join(UserModel, UserModel.id == SessionModel.user_persist_id)
    )
    async with get_session() as db_session:
        records = (await db_session.scalars(statement)).all()
    return records
