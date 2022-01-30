import time
from typing import Any, Dict, Optional
from sqlmodel.ext.asyncio.session import AsyncSession

from nonebot.typing import T_CalledAPIHook
from nonebot.message import event_postprocessor
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    GroupMessageEvent,
)
from nonebot_plugin_datastore import get_session

from .model import MessageRecord


session: AsyncSession = None


@event_postprocessor
async def _(bot: Bot, event: MessageEvent):

    record = MessageRecord(
        platform="qq",
        time=event.time,
        type="message",
        detail_type="group" if isinstance(event, GroupMessageEvent) else "private",
        message_id=str(event.message_id),
        message=[{"type": seg.type, "data": seg.data} for seg in event.message],
        alt_message=str(event.get_message()),
        self_id=str(bot.self_id),
        user_id=str(event.user_id),
        group_id=str(event.group_id) if isinstance(event, GroupMessageEvent) else "",
    )

    global session
    if not session:
        session = await get_session()
    session.add(record)
    await session.commit()


@Bot.on_called_api
async def _(
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
        or (api == "send_msg" and data.get["message_type"] == "group")
        else "private",
        message_id=str(result["message_id"]),
        message=[
            {"type": seg.type, "data": seg.data} for seg in Message(data["message"])
        ],
        alt_message=data["message"],
        self_id=str(bot.self_id),
        user_id=str(data["user_id"]),
        group_id=str(data.get("group_id", "")),
    )

    global session
    if not session:
        session = await get_session()
    session.add(record)
    await session.commit()
