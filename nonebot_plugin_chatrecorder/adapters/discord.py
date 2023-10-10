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
    from nonebot.adapters.discord import Bot, Message, MessageEvent
    from nonebot.adapters.discord.api import UNSET, Channel, ChannelType, MessageGet

    adapter = SupportedAdapter.discord

    @event_postprocessor
    async def record_recv_msg(bot: Bot, event: MessageEvent):
        session = extract_session(bot, event)
        session_persist_id = await get_session_persist_id(session)

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=remove_timezone(event.timestamp),
            type=event.get_type(),
            message_id=str(event.id),
            message=serialize_message(adapter, event.get_message()),
            plain_text=event.get_plaintext(),
        )
        async with get_session() as db_session:
            db_session.add(record)
            await db_session.commit()

    _channel_cache: Dict[int, Channel] = {}

    async def get_channel(bot: Bot, channel_id: int) -> Channel:
        if channel_id in _channel_cache:
            return _channel_cache[channel_id]
        channel = await bot.get_channel(channel_id=channel_id)
        _channel_cache[channel_id] = channel
        return channel

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
            if api not in ["create_message"]:
                return
            if not isinstance(result, MessageGet):
                return

            channel = await get_channel(bot, result.channel_id)

            level = SessionLevel.LEVEL0
            id1 = None
            id2 = str(result.channel_id)
            id3 = None
            if channel.type in [ChannelType.DM]:
                level = SessionLevel.LEVEL1
                id1 = (
                    str(channel.recipients[0].id)
                    if channel.recipients != UNSET and channel.recipients
                    else None
                )
            else:
                level = SessionLevel.LEVEL3
                id3 = str(channel.guild_id) if channel.guild_id != UNSET else None

            session = Session(
                bot_id=bot.self_id,
                bot_type=bot.type,
                platform=SupportedPlatform.discord,
                level=level,
                id1=id1,
                id2=id2,
                id3=id3,
            )
            session_persist_id = await get_session_persist_id(session)

            message = Message.from_guild_message(result)
            record = MessageRecord(
                session_persist_id=session_persist_id,
                time=remove_timezone(result.timestamp),
                type="message_sent",
                message_id=str(result.id),
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
