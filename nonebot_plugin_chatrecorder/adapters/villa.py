from datetime import datetime
from typing import Any, Dict, Optional, Type, Union

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

try:
    from nonebot.adapters.villa import Bot, Message, SendMessageEvent
    from nonebot.adapters.villa.models import MessageContentInfo

    adapter = SupportedAdapter.villa

    @event_postprocessor
    async def record_recv_msg(bot: Bot, event: SendMessageEvent):
        session = extract_session(bot, event)
        session_persist_id = await get_session_persist_id(session)

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=datetime.utcfromtimestamp(event.send_at / 1000),
            type=event.get_type(),
            message_id=event.msg_uid,
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
            result: Optional[Any],
        ):
            if not isinstance(bot, Bot):
                return
            if e or not result:
                return
            if api not in ["send_message"]:
                return

            msg_content: Union[str, MessageContentInfo] = data["msg_content"]
            if isinstance(msg_content, str):
                msg_content = MessageContentInfo.parse_raw(msg_content)
            message = Message.from_message_content_info(msg_content)

            session = Session(
                bot_id=bot.self_id,
                bot_type=bot.type,
                platform=SupportedPlatform.villa,
                level=SessionLevel.LEVEL3,
                id1=None,
                id2=str(data["room_id"]),
                id3=str(data["villa_id"]),
            )
            session_persist_id = await get_session_persist_id(session)

            record = MessageRecord(
                session_persist_id=session_persist_id,
                time=datetime.utcnow(),
                type="message_sent",
                message_id=str(result),
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
