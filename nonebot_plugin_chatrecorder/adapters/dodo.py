from datetime import datetime, timezone
from typing import Any, Optional

from nonebot.adapters import Bot as BaseBot
from nonebot.message import event_postprocessor
from nonebot_plugin_orm import get_session
from nonebot_plugin_session import Session, SessionLevel, extract_session
from nonebot_plugin_session_orm import get_session_persist_id
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
from ..utils import record_type, remove_timezone

try:
    from nonebot.adapters.dodo import Bot, Message, MessageEvent
    from nonebot.adapters.dodo.models import MessageReturn

    adapter = SupportedAdapter.dodo

    @event_postprocessor
    async def record_recv_msg(bot: Bot, event: MessageEvent):
        session = extract_session(bot, event)
        session_persist_id = await get_session_persist_id(session)

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=remove_timezone(event.timestamp),
            type=record_type(event),
            message_id=event.message_id,
            message=serialize_message(adapter, event.get_message()),
            plain_text=event.get_plaintext(),
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
            data: dict[str, Any],
            result: Any,
        ):
            if not isinstance(bot, Bot):
                return
            if e or not result or not isinstance(result, MessageReturn):
                return

            island_source_id = None
            channel_id = None
            if api == "set_channel_message_send":
                level = SessionLevel.LEVEL3
                channel_id = data["channel_id"]
                dodo_source_id = data.get("dodo_source_id")
            elif api == "set_personal_message_send":
                level = SessionLevel.LEVEL1
                island_source_id = data["island_source_id"]
                dodo_source_id = data["dodo_source_id"]
            else:
                return

            message = Message.from_message_body(data["message_body"])

            session = Session(
                bot_id=bot.self_id,
                bot_type=bot.type,
                platform=SupportedPlatform.dodo,
                level=level,
                id1=dodo_source_id,
                id2=channel_id,
                id3=island_source_id,
            )
            session_persist_id = await get_session_persist_id(session)

            record = MessageRecord(
                session_persist_id=session_persist_id,
                time=remove_timezone(datetime.now(timezone.utc)),
                type="message_sent",
                message_id=result.message_id,
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
        def get_message_class(cls) -> type[Message]:
            return Message

    register_serializer(adapter, Serializer)
    register_deserializer(adapter, Deserializer)

except ImportError:
    pass
