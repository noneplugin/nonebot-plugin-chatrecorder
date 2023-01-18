from sqlmodel import Field
from typing import Optional
from datetime import datetime

from nonebot_plugin_datastore import get_plugin_data

Model = get_plugin_data().Model


class MessageRecord(Model, table=True):
    """消息记录"""

    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    bot_type: str
    """ 协议适配器名称 """
    bot_id: str
    """ 机器人id """
    platform: str
    """ 机器人平台名称 """
    time: datetime
    """ 消息时间\n\n存放 UTC 时间 """
    type: str
    """ 事件类型\n\n此处主要包含 `message` 和 `message_sent` 两种\n\n`message_sent` 是 bot 发出的消息"""
    detail_type: str
    """ 具体事件类型 """
    message_id: str
    """ 消息id """
    message: str
    """ 消息内容
    存放 onebot 消息段的字符串
    """
    plain_text: str
    """ 消息内容的纯文本形式
    存放纯文本消息（忽略非纯文本消息段）
    """
    user_id: str
    """ 用户id """
    group_id: Optional[str] = None
    """ 群组id """
    guild_id: Optional[str] = None
    """ 两级群组消息中的 群组id """
    channel_id: Optional[str] = None
    """ 两级群组消息中的 频道id """
