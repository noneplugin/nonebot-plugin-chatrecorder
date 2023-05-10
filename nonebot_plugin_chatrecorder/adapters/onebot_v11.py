from datetime import datetime
from typing import Any, Dict, Optional

from nonebot.adapters import Bot as BaseBot
from nonebot.message import event_postprocessor
from nonebot_plugin_datastore import create_session

from ..config import plugin_config
from ..message import serialize_message
from ..model import MessageRecord

try:
    from nonebot.adapters.onebot.v11 import (
        Bot,
        GroupMessageEvent,
        Message,
        MessageEvent,
    )

    @event_postprocessor
    async def record_recv_msg(bot: Bot, event: MessageEvent):
        record = MessageRecord(
            bot_type=bot.type,
            bot_id=bot.self_id,
            platform="qq",
            time=datetime.utcfromtimestamp(event.time),
            type=event.post_type,
            detail_type=event.message_type,
            message_id=str(event.message_id),
            message=serialize_message(event.message),
            plain_text=event.message.extract_plain_text(),
            user_id=str(event.user_id),
            group_id=str(event.group_id)
            if isinstance(event, GroupMessageEvent)
            else None,
        )

        async with create_session() as session:
            session.add(record)
            await session.commit()

    if plugin_config.chatrecorder_record_send_msg:

        @Bot.on_called_api
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
                bot_type=bot.type,
                bot_id=bot.self_id,
                platform="qq",
                time=datetime.utcnow(),
                type="message_sent",
                detail_type="group"
                if api == "send_group_msg"
                or (api == "send_msg" and data["message_type"] == "group")
                else "private",
                message_id=str(result["message_id"]),
                message=serialize_message(message),
                plain_text=message.extract_plain_text(),
                user_id=str(bot.self_id),
                group_id=str(data.get("group_id", "")) or None,
            )

            async with create_session() as session:
                session.add(record)
                await session.commit()

except ImportError:
    pass
