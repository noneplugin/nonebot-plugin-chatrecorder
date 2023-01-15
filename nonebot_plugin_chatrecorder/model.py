from datetime import datetime
from typing import Optional

from nonebot_plugin_datastore import get_plugin_data
from sqlmodel import Field

Model = get_plugin_data().Model


class MessageRecord(Model, table=True):
    """消息记录"""

    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    platform: str
    time: datetime
    """ 消息时间
    存放 UTC 时间
    """
    type: str
    detail_type: str
    message_id: str
    message: str
    """ 消息内容
    存放 onebot 消息段的字符串
    """
    alt_message: str
    """ 消息内容的替代表示
    存放纯文本消息
    """
    user_id: str
    group_id: Optional[str] = ""
