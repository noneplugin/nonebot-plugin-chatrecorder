from datetime import datetime

from nonebot_plugin_datastore import get_plugin_data
from nonebot_plugin_session.model import SessionModel
from sqlalchemy import JSON, TEXT, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .message import JsonMsg

plugin_data = get_plugin_data()
plugin_data.use_global_registry()
Model = plugin_data.Model


class MessageRecord(Model):
    """消息记录"""

    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("nonebot_plugin_session_sessionmodel.id")
    )
    session: Mapped[SessionModel] = relationship(back_populates="message_records")
    """ 会话属性 """
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


SessionModel.message_records = relationship(MessageRecord, back_populates="session")
