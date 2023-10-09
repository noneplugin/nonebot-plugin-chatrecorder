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
    from nonebot.adapters.kaiheila import Bot, Message, MessageSegment
    from nonebot.adapters.kaiheila.api.model import MessageCreateReturn
    from nonebot.adapters.kaiheila.event import MessageEvent
    from nonebot.adapters.kaiheila.message import rev_msg_type_map

    adapter = SupportedAdapter.kaiheila

    @event_postprocessor
    async def record_recv_msg(bot: Bot, event: MessageEvent):
        session = extract_session(bot, event)
        session_persist_id = await get_session_persist_id(session)

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=datetime.utcfromtimestamp(event.msg_timestamp / 1000),
            type=event.post_type,
            message_id=event.msg_id,
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
            if not (
                isinstance(result, MessageCreateReturn)
                and result.msg_id
                and result.msg_timestamp
            ):
                return

            if api == "message/create":
                level = SessionLevel.LEVEL3
                channel_id = data["target_id"]
                user_id = data.get("temp_target_id")
            elif api == "direct-message/create":
                level = SessionLevel.LEVEL1
                channel_id = None
                user_id = data["target_id"]
            else:
                return

            type_code = data["type"]
            content = data["content"]
            type = rev_msg_type_map.get(type_code, "")
            if type == "text":
                message = MessageSegment.text(content)
            elif type == "image":
                message = MessageSegment.image(content)
            elif type == "video":
                message = MessageSegment.video(content)
            elif type == "file":
                message = MessageSegment.file(content)
            elif type == "audio":
                message = MessageSegment.audio(content)
            elif type == "kmarkdown":
                message = MessageSegment.KMarkdown(content)
            elif type == "card":
                message = MessageSegment.Card(content)
            else:
                message = MessageSegment(type, {"content": content})
            message = Message(message)

            session = Session(
                bot_id=bot.self_id,
                bot_type=bot.type,
                platform=SupportedPlatform.kaiheila,
                level=level,
                id1=user_id,
                id2=None,
                id3=channel_id,
            )
            session_persist_id = await get_session_persist_id(session)

            record = MessageRecord(
                session_persist_id=session_persist_id,
                time=datetime.utcfromtimestamp(result.msg_timestamp / 1000),
                type="message_sent",
                message_id=result.msg_id,
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
