from datetime import datetime
from typing import Any, Dict, Optional

from nonebot import get_driver, require
from nonebot.adapters import Bot as BaseBot
from nonebot.message import event_postprocessor
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    GroupMessageEvent,
)

require("nonebot_plugin_datastore")
from nonebot_plugin_datastore import create_session

from .model import MessageRecord
from .message import serialize_message
from .config import Config
from .record import get_message_records


@event_postprocessor
async def record_recv_msg(event: MessageEvent):

    record = MessageRecord(
        platform="qq",
        time=datetime.utcfromtimestamp(event.time),
        type="message",
        detail_type="group" if isinstance(event, GroupMessageEvent) else "private",
        message_id=str(event.message_id),
        message=serialize_message(event.message),
        alt_message=event.message.extract_plain_text(),
        user_id=str(event.user_id),
        group_id=str(event.group_id) if isinstance(event, GroupMessageEvent) else "",
    )

    async with create_session() as session:
        session.add(record)
        await session.commit()


async def record_send_msg(
    bot: BaseBot,
    e: Optional[Exception],
    api: str,
    data: Dict[str, Any],
    result: Optional[Dict[str, Any]],
):

    if e or not result:
        return
    if api not in ["send_msg", "send_private_msg", "send_group_msg"]:
        return

    message = Message(data["message"])
    record = MessageRecord(
        platform="qq",
        time=datetime.utcnow(),
        type="message",
        detail_type="group"
        if api == "send_group_msg"
        or (api == "send_msg" and data["message_type"] == "group")
        else "private",
        message_id=str(result["message_id"]),
        message=serialize_message(message),
        alt_message=message.extract_plain_text(),
        user_id=str(bot.self_id),
        group_id=str(data.get("group_id", "")),
    )

    async with create_session() as session:
        session.add(record)
        await session.commit()


plugin_config = Config.parse_obj(get_driver().config.dict())
if plugin_config.chatrecorder_record_send_msg:
    Bot.on_called_api(record_send_msg)
