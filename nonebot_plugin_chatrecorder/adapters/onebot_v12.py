from datetime import datetime
from typing import Any, Dict, Optional, Type

from nonebot.adapters import Bot as BaseBot
from nonebot.message import event_postprocessor
from nonebot_plugin_orm import get_session
from nonebot_plugin_session import Session, SessionLevel, extract_session
from nonebot_plugin_session_orm import get_session_persist_id
from typing_extensions import override

from ..config import plugin_config
from ..consts import SupportedAdapter
from ..message import (
    MessageDeserializer,
    MessageSerializer,
    register_deserializer,
    register_serializer,
    serialize_message,
)
from ..model import MessageRecord

try:
    from nonebot.adapters.onebot.v12 import Bot, Message, MessageEvent

    adapter = SupportedAdapter.onebot_v12

    @event_postprocessor
    async def record_recv_msg(bot: Bot, event: MessageEvent):
        session = extract_session(bot, event)
        session_persist_id = await get_session_persist_id(session)

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=event.time,
            type=event.type,
            message_id=event.message_id,
            message=serialize_message(adapter, event.message),
            plain_text=event.message.extract_plain_text(),
        )
        async with get_session() as db_session:
            db_session.add(record)
            await db_session.commit()

    if plugin_config.chatrecorder_record_send_msg:

        @Bot.on_called_api
        async def record_send_msg(
            bot: BaseBot,
            e: Optional[Exception],
            api: str,
            data: Dict[str, Any],
            result: Optional[Dict[str, Any]],
        ):
            if not isinstance(bot, Bot):
                return
            if e or not result:
                return
            if api not in ["send_message"]:
                return

            detail_type = data["detail_type"]
            level = SessionLevel.LEVEL0
            if detail_type == "channel":
                level = SessionLevel.LEVEL3
            elif detail_type == "group":
                level = SessionLevel.LEVEL2
            elif detail_type == "private":
                level = SessionLevel.LEVEL1

            session = Session(
                bot_id=bot.self_id,
                bot_type=bot.type,
                platform=bot.platform,
                level=level,
                id1=data.get("user_id"),
                id2=data.get("group_id") or data.get("channel_id"),
                id3=data.get("guild_id"),
            )
            session_persist_id = await get_session_persist_id(session)

            message = Message(data["message"])
            record = MessageRecord(
                session_persist_id=session_persist_id,
                time=datetime.utcfromtimestamp(result["time"]),
                type="message_sent",
                message_id=result["message_id"],
                message=serialize_message(adapter, message),
                plain_text=message.extract_plain_text(),
            )
            async with get_session() as db_session:
                db_session.add(record)
                await db_session.commit()

    class Serializer(MessageSerializer[Message]):
        pass

    class Deserializer(MessageDeserializer[Message]):
        @classmethod
        @override
        def get_message_class(cls) -> Type[Message]:
            return Message

    register_serializer(adapter, Serializer)
    register_deserializer(adapter, Deserializer)

except ImportError:
    pass
