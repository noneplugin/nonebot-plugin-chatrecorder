from datetime import datetime
from typing import Any, Dict, Optional

from nonebot import get_driver, require
from nonebot.adapters import Bot as BaseBot
from nonebot.message import event_postprocessor

from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v11 import Message as V11Msg
from nonebot.adapters.onebot.v11 import MessageEvent as V11MEvent
from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GMEvent

from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot.adapters.onebot.v12 import Message as V12Msg
from nonebot.adapters.onebot.v12 import MessageEvent as V12MEvent
from nonebot.adapters.onebot.v12 import GroupMessageEvent as V12GMEvent
from nonebot.adapters.onebot.v12 import ChannelMessageEvent as V12CMEvent

require("nonebot_plugin_datastore")
from nonebot_plugin_datastore import create_session

from .config import Config
from .model import MessageRecord
from .message import serialize_message
from .record import get_message_records, get_messages, get_messages_plain_text

plugin_config = Config.parse_obj(get_driver().config.dict())


@event_postprocessor
async def record_recv_msg_v11(bot: V11Bot, event: V11MEvent):
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
        group_id=str(event.group_id) if isinstance(event, V11GMEvent) else None,
    )

    async with create_session() as session:
        session.add(record)
        await session.commit()


@event_postprocessor
async def record_recv_msg_v12(bot: V12Bot, event: V12MEvent):
    record = MessageRecord(
        bot_type=bot.type,
        bot_id=bot.self_id,
        platform=bot.platform,
        time=event.time,
        type=event.type,
        detail_type=event.detail_type,
        message_id=event.message_id,
        message=serialize_message(event.message),
        plain_text=event.message.extract_plain_text(),
        user_id=event.user_id,
        group_id=event.group_id if isinstance(event, V12GMEvent) else None,
        guild_id=event.guild_id if isinstance(event, V12CMEvent) else None,
        channel_id=event.channel_id if isinstance(event, V12CMEvent) else None,
    )

    async with create_session() as session:
        session.add(record)
        await session.commit()


if plugin_config.chatrecorder_record_send_msg:

    @V11Bot.on_called_api
    async def record_send_msg_v11(
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

        message = V11Msg(data["message"])
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

    @V12Bot.on_called_api
    async def record_send_msg_v12(
        bot: BaseBot,
        e: Optional[Exception],
        api: str,
        data: Dict[str, Any],
        result: Optional[Dict[str, Any]],
    ):
        if e or not result:
            return
        if api not in ["send_message"]:
            return
        assert isinstance(bot, V12Bot)

        message = V12Msg(data["message"])
        record = MessageRecord(
            bot_type=bot.type,
            bot_id=bot.self_id,
            platform=bot.platform,
            time=datetime.utcfromtimestamp(result["time"]),
            type="message_sent",
            detail_type=data["detail_type"],
            message_id=result["message_id"],
            message=serialize_message(message),
            plain_text=message.extract_plain_text(),
            user_id=str(bot.self_id),
            group_id=data.get("group_id"),
            guild_id=data.get("guild_id"),
            channel_id=data.get("channel_id"),
        )

        async with create_session() as session:
            session.add(record)
            await session.commit()
