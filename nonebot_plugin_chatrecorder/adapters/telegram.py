from datetime import datetime
from typing import Any, Dict, Optional, Type

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
    from nonebot.adapters.telegram import Bot, Message
    from nonebot.adapters.telegram.event import MessageEvent
    from nonebot.adapters.telegram.model import Message as TGMessage

    adapter = SupportedAdapter.telegram

    @event_postprocessor
    async def record_recv_msg(bot: Bot, event: MessageEvent):
        session = extract_session(bot, event)
        session_persist_id = await get_session_persist_id(session)

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=datetime.utcfromtimestamp(event.date),
            type=event.get_type(),
            message_id=f"{event.chat.id}_{event.message_id}",
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
            if e or not result:
                return

            if api in [
                "send_message",
                "send_photo",
                "send_audio",
                "send_document",
                "send_video",
                "send_animation",
                "send_voice",
                "send_video_note",
                "send_location",
                "send_venue",
                "send_contact",
                "send_poll",
                "send_dice",
                "send_sticker",
                "send_invoice",
            ]:
                tg_message = TGMessage.parse_obj(result)
                chat = tg_message.chat
                message_id = f"{chat.id}_{tg_message.message_id}"
                message = Message.parse_obj(result)

            elif api == "send_media_group":
                tg_messages = [TGMessage.parse_obj(res) for res in result]
                tg_message = tg_messages[0]
                chat = tg_message.chat
                message_id = "_".join([str(msg.message_id) for msg in tg_messages])
                message_id = f"{chat.id}_{message_id}"
                message = Message()
                for res in result:
                    message += Message.parse_obj(res)

            else:
                return

            message_thread_id = tg_message.message_thread_id
            chat_id = tg_message.chat.id
            id1 = None
            id2 = None
            id3 = None
            if message_thread_id:
                id3 = str(chat_id)
                id2 = str(message_thread_id)
                level = SessionLevel.LEVEL3
            elif chat.type == "private":
                id1 = str(chat_id)
                level = SessionLevel.LEVEL1
            else:
                id2 = str(chat_id)
                level = SessionLevel.LEVEL2

            session = Session(
                bot_id=bot.self_id,
                bot_type=bot.type,
                platform=SupportedPlatform.telegram,
                level=level,
                id1=id1,
                id2=id2,
                id3=id3,
            )
            session_persist_id = await get_session_persist_id(session)

            record = MessageRecord(
                session_persist_id=session_persist_id,
                time=datetime.utcfromtimestamp(tg_message.date),
                type="message_sent",
                message_id=message_id,
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
