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
from ..utils import remove_timezone

try:
    from nonebot.adapters.qqguild import Bot, Message, MessageEvent
    from nonebot.adapters.qqguild.api.model import Message as GuildMessage

    adapter = SupportedAdapter.qqguild

    @event_postprocessor
    async def record_recv_msg(bot: Bot, event: MessageEvent):
        session = extract_session(bot, event)
        session_persist_id = await get_session_persist_id(session)

        assert event.id
        assert event.timestamp

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=remove_timezone(event.timestamp),
            type=event.get_type(),
            message_id=event.id,
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
            data: Dict[str, Any],
            result: Any,
        ):
            if not isinstance(bot, Bot):
                return
            if e or not result:
                return
            if not isinstance(result, GuildMessage):
                return

            id1 = None
            id2 = None
            id3 = None
            if api == "post_messages":
                level = SessionLevel.LEVEL3
                assert result.guild_id
                assert result.channel_id
                id3 = str(result.guild_id)
                id2 = str(result.channel_id)
            elif api == "post_dms_messages":
                # TODO "post_dms_messages" 的返回值是什么样的？
                # 是否应该存 src_guild_id 和 recipient_id？
                level = SessionLevel.LEVEL1
                assert result.guild_id
                id3 = str(result.guild_id)
            else:
                return

            session = Session(
                bot_id=bot.self_id,
                bot_type=bot.type,
                platform=SupportedPlatform.qqguild,
                level=level,
                id1=id1,
                id2=id2,
                id3=id3,
            )
            session_persist_id = await get_session_persist_id(session)

            assert result.id
            assert result.timestamp
            message = Message.from_guild_message(result)

            record = MessageRecord(
                session_persist_id=session_persist_id,
                time=remove_timezone(result.timestamp),
                type="message_sent",
                message_id=result.id,
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
