from dataclasses import asdict
from datetime import datetime, timezone
from itertools import count
from typing import Any, Dict, Optional, Type

from nonebot.adapters import Bot as BaseBot
from nonebot.message import event_postprocessor
from nonebot_plugin_orm import get_session
from nonebot_plugin_session import Session, SessionLevel, extract_session
from nonebot_plugin_session_orm import SessionModel, get_session_persist_id
from typing_extensions import override

from ..config import plugin_config
from ..consts import SupportedAdapter, SupportedPlatform
from ..message import (
    MessageDeserializer,
    MessageSerializer,
    register_deserializer,
    register_serializer,
    serialize_message,
)
from ..model import MessageRecord
from ..utils import remove_timezone

try:
    from nonebot.adapters.console import Bot, Message, MessageEvent, MessageSegment
    from nonechat import ConsoleMessage, Emoji, Text
    from sqlalchemy import select

    adapter = SupportedAdapter.console

    id = None

    async def get_id() -> str:
        global id
        if not id:
            statement = (
                select(MessageRecord.message_id)
                .where(SessionModel.bot_type == adapter)
                .order_by(MessageRecord.message_id.desc())
                .join(SessionModel, SessionModel.id == MessageRecord.session_persist_id)
            )
            async with get_session() as db_session:
                message_id = await db_session.scalar(statement)
            id = count(int(message_id) + 1) if message_id else count(0)
        return str(next(id))

    @event_postprocessor
    async def record_recv_msg(bot: Bot, event: MessageEvent):
        session = extract_session(bot, event)
        session_persist_id = await get_session_persist_id(session)

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=remove_timezone(event.time.astimezone(timezone.utc)),
            type=event.post_type,
            message_id=await get_id(),
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
            result: Any,
        ):
            if not isinstance(bot, Bot):
                return
            if e or api not in ["send_msg"]:
                return

            session = Session(
                bot_id=bot.self_id,
                bot_type=bot.type,
                platform=SupportedPlatform.console,
                level=SessionLevel.LEVEL1,
                id1=data.get("user_id"),
                id2=None,
                id3=None,
            )
            session_persist_id = await get_session_persist_id(session)

            elements = ConsoleMessage(data["message"])
            message = Message()
            for elem in elements:
                if isinstance(elem, Text):
                    message += MessageSegment.text(elem.text)
                elif isinstance(elem, Emoji):
                    message += MessageSegment.emoji(elem.name)
                else:
                    message += MessageSegment(
                        type=elem.__class__.__name__.lower(), data=asdict(elem)  # type: ignore
                    )

            record = MessageRecord(
                session_persist_id=session_persist_id,
                time=datetime.utcnow(),
                type="message_sent",
                message_id=await get_id(),
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
