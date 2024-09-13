from datetime import datetime, timezone
from typing import Any, Optional

from nonebot.adapters import Bot as BaseBot
from nonebot.compat import type_validate_python
from nonebot.message import event_postprocessor
from nonebot_plugin_orm import get_session
from nonebot_plugin_session import Session, SessionLevel, extract_session
from nonebot_plugin_session_orm import get_session_persist_id
from pydantic import ValidationError
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
    from nonebot.adapters.red import Bot, Message, MessageEvent
    from nonebot.adapters.red.api.model import ChatType
    from nonebot.adapters.red.api.model import Message as MessageModel

    adapter = SupportedAdapter.red

    @event_postprocessor
    async def record_recv_msg(bot: Bot, event: MessageEvent):
        session = extract_session(bot, event)
        session_persist_id = await get_session_persist_id(session)

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=remove_timezone(
                datetime.fromtimestamp(int(event.msgTime), timezone.utc)
            ),
            type=record_type(event),
            message_id=event.msgId,
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
            if e or not result:
                return
            if api not in ["send_message"]:
                return

            try:
                resp = type_validate_python(MessageModel, result)
            except ValidationError:
                return
            if not resp.elements:
                return
            peer_uin = resp.peerUin or resp.peerUid
            if not peer_uin:
                return

            id1 = None
            id2 = None
            level = SessionLevel.LEVEL0
            if resp.chatType == ChatType.GROUP:
                id2 = peer_uin
                level = SessionLevel.LEVEL2
            elif resp.chatType == ChatType.FRIEND:
                id1 = peer_uin
                level = SessionLevel.LEVEL1

            session = Session(
                bot_id=bot.self_id,
                bot_type=bot.type,
                platform=SupportedPlatform.qq,
                level=level,
                id1=id1,
                id2=id2,
            )
            session_persist_id = await get_session_persist_id(session)

            message = Message.from_red_message(
                resp.elements, resp.msgId, resp.chatType, peer_uin
            )
            record = MessageRecord(
                session_persist_id=session_persist_id,
                time=remove_timezone(
                    datetime.fromtimestamp(int(resp.msgTime), timezone.utc)
                ),
                type="message_sent",
                message_id=resp.msgId,
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
