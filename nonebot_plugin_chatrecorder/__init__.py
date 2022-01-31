import time
from typing import Any, Dict, Optional

import nonebot
from nonebot import get_driver
from nonebot.plugin import export
from nonebot.typing import T_CalledAPIHook
from nonebot.message import event_postprocessor
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    GroupMessageEvent,
)

from .model import MessageRecord, session
from .message import serialize_message
from .condig import Config
from .record import get_message_records

export.get_message_records = get_message_records


@event_postprocessor
async def record_recv_msg(event: MessageEvent):

    record = MessageRecord(
        platform="qq",
        time=event.time,
        type="message",
        detail_type="group" if isinstance(event, GroupMessageEvent) else "private",
        message_id=str(event.message_id),
        message=serialize_message(event.message),
        user_id=str(event.user_id),
        group_id=str(event.group_id) if isinstance(event, GroupMessageEvent) else "",
    )
    session.add(record)
    await session.commit()


async def record_send_msg(
    bot: Bot,
    e: Exception,
    api: str,
    data: Dict[str, Any],
    result: Optional[Dict[str, Any]],
) -> T_CalledAPIHook:

    if e or not result:
        return
    if api not in ["send_msg", "send_private_msg", "send_group_msg"]:
        return

    record = MessageRecord(
        platform="qq",
        time=int(time.time()),
        type="message",
        detail_type="group"
        if api == "send_group_msg"
        or (api == "send_msg" and data["message_type"] == "group")
        else "private",
        message_id=str(result["message_id"]),
        message=serialize_message(Message(data["message"])),
        user_id=str(bot.self_id),
        group_id=str(data.get("group_id", "")),
    )
    session.add(record)
    await session.commit()


plugin_config = Config.parse_obj(get_driver().config.dict())
if plugin_config.chatrecorder_record_send_msg:
    Bot.on_called_api(record_send_msg)


nonebot.get_driver().on_shutdown(lambda _: session.close())
