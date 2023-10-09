import json
import re
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
    from nonebot.adapters.feishu import Bot, Message
    from nonebot.adapters.feishu import MessageDeserializer as FeishuMessageDeserializer
    from nonebot.adapters.feishu import MessageEvent

    adapter = SupportedAdapter.feishu

    @event_postprocessor
    async def record_recv_msg(bot: Bot, event: MessageEvent):
        session = extract_session(bot, event)
        session_persist_id = await get_session_persist_id(session)

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=datetime.utcfromtimestamp(int(event.event.message.create_time) / 1000),
            type=event.get_type(),
            message_id=event.event.message.message_id,
            message=serialize_message(adapter, event.get_message()),
            plain_text=event.get_message().extract_plain_text(),
        )
        async with get_session() as db_session:
            db_session.add(record)
            await db_session.commit()

    _chat_info_cache: Dict[str, Dict[str, Any]] = {}

    async def get_chat_info(bot: Bot, chat_id: str) -> Dict[str, Any]:
        if chat_id in _chat_info_cache:
            return _chat_info_cache[chat_id]
        params = {"method": "GET", "query": {"user_id_type": "open_id"}}
        resp = await bot.call_api(f"im/v1/chats/{chat_id}", **params)
        _chat_info_cache[chat_id] = resp
        return resp

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
                api == "im/v1/messages" or re.match(r"im/v1/messages/\S+/reply", api)
            ):
                return

            chat_id = result["chat_id"]
            resp = await get_chat_info(bot, chat_id)
            chat_mode = resp["chat_mode"]

            level = SessionLevel.LEVEL0
            id1 = None
            id2 = None
            if chat_mode == "p2p":
                level = SessionLevel.LEVEL1
                id1 = resp["owner_id"]
            elif chat_mode == "group":
                level = SessionLevel.LEVEL2
                id2 = chat_id

            session = Session(
                bot_id=bot.self_id,
                bot_type=bot.type,
                platform=SupportedPlatform.feishu,
                level=level,
                id1=id1,
                id2=id2,
                id3=None,
            )
            session_persist_id = await get_session_persist_id(session)

            msg_type = result["msg_type"]
            content = result["body"]["content"]
            mentions = result.get("mentions")
            message = FeishuMessageDeserializer(
                msg_type, json.loads(content), mentions
            ).deserialize()

            record = MessageRecord(
                session_persist_id=session_persist_id,
                time=datetime.utcfromtimestamp(int(result["create_time"]) / 1000),
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
