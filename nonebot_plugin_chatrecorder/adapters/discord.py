from typing import Any, Optional

from nonebot.adapters import Bot as BaseBot
from nonebot.message import event_postprocessor
from nonebot_plugin_orm import get_session
from nonebot_plugin_uninfo import (
    Scene,
    SceneType,
    Session,
    SupportAdapter,
    SupportScope,
    Uninfo,
    User,
)
from nonebot_plugin_uninfo.orm import get_session_persist_id
from typing_extensions import override

from ..config import plugin_config
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
    from nonebot.adapters.discord import Bot, Message, MessageEvent
    from nonebot.adapters.discord.api import UNSET, Channel, ChannelType, MessageGet

    adapter = SupportAdapter.discord

    @event_postprocessor
    async def record_recv_msg(event: MessageEvent, session: Uninfo):
        session_persist_id = await get_session_persist_id(session)

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=remove_timezone(event.timestamp),
            type=record_type(event),
            message_id=str(event.id),
            message=serialize_message(adapter, event.get_message()),
            plain_text=event.get_plaintext(),
        )
        async with get_session() as db_session:
            db_session.add(record)
            await db_session.commit()

    _channel_cache: dict[int, Channel] = {}

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
            data: dict[str, Any],
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

            if channel.type in [ChannelType.DM]:
                scene_type = SceneType.PRIVATE
                scene_id = (
                    str(channel.recipients[0].id)
                    if channel.recipients != UNSET and channel.recipients
                    else ""
                )
            else:
                scene_type = SceneType.CHANNEL_TEXT
                scene_id = str(channel.guild_id) if channel.guild_id != UNSET else ""

            session = Session(
                self_id=bot.self_id,
                adapter=adapter,
                scope=SupportScope.discord,
                scene=Scene(id=scene_id, type=scene_type),
                user=User(id=bot.self_id),
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
        def get_message_class(cls) -> type[Message]:
            return Message

    register_serializer(adapter, Serializer)
    register_deserializer(adapter, Deserializer)

except ImportError:
    pass
