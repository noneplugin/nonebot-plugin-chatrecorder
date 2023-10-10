from datetime import datetime

from nonebot_plugin_orm import Model
from sqlalchemy import JSON, TEXT, String
from sqlalchemy.orm import Mapped, mapped_column

from .message import JsonMsg


class MessageRecord(Model):
    """消息记录"""

    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    session_persist_id: Mapped[int]
    """ 会话持久化id """
    time: Mapped[datetime]
    """ 消息时间\n\n存放 UTC 时间 """
    type: Mapped[str] = mapped_column(String(32))
    """ 消息类型\n\n此处主要包含 `message` 和 `message_sent` 两种\n\n`message_sent` 是 bot 发出的消息"""
    message_id: Mapped[str] = mapped_column(String(64))
    """ 消息id """
    message: Mapped[JsonMsg] = mapped_column(JSON)
    """ 消息内容
    存放 onebot 消息段
    """
    plain_text: Mapped[str] = mapped_column(TEXT)
    """ 消息内容的纯文本形式
    存放纯文本消息（忽略非纯文本消息段）
    """
