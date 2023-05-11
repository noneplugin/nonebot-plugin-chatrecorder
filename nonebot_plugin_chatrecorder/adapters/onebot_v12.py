from datetime import datetime
from typing import Any, Dict, Optional, Type

from nonebot.adapters import Bot as BaseBot
from nonebot.message import event_postprocessor
from nonebot.typing import overrides
from nonebot_plugin_datastore import create_session

from ..config import plugin_config
from ..model import MessageRecord
from .consts import SupportedAdapter
from .message import (
    MessageDeserializer,
    MessageSerializer,
    register_deserializer,
    register_serializer,
    serialize_message,
)

try:
    from nonebot.adapters.onebot.v12 import (
        Bot,
        ChannelMessageEvent,
        GroupMessageEvent,
        Message,
        MessageEvent,
    )

    @event_postprocessor
    async def record_recv_msg(bot: Bot, event: MessageEvent):
        record = MessageRecord(
            bot_type=bot.type,
            bot_id=bot.self_id,
            platform=bot.platform,
            time=event.time,
            type=event.type,
            detail_type=event.detail_type,
            message_id=event.message_id,
            message=serialize_message(bot, event.message),
            plain_text=event.message.extract_plain_text(),
            user_id=event.user_id,
            group_id=event.group_id if isinstance(event, GroupMessageEvent) else None,
            guild_id=event.guild_id if isinstance(event, ChannelMessageEvent) else None,
            channel_id=event.channel_id
            if isinstance(event, ChannelMessageEvent)
            else None,
        )

        async with create_session() as session:
            session.add(record)
            await session.commit()

    if plugin_config.chatrecorder_record_send_msg:

        @Bot.on_called_api
        async def record_send_msg(
            bot: BaseBot,
            e: Optional[Exception],
            api: str,
            data: Dict[str, Any],
            result: Optional[Dict[str, Any]],
        ):
            if e or not result:
                return
            if api not in ["send_message"]:
                return
            assert isinstance(bot, Bot)

            message = Message(data["message"])
            record = MessageRecord(
                bot_type=bot.type,
                bot_id=bot.self_id,
                platform=bot.platform,
                time=datetime.utcfromtimestamp(result["time"]),
                type="message_sent",
                detail_type=data["detail_type"],
                message_id=result["message_id"],
                message=serialize_message(bot, message),
                plain_text=message.extract_plain_text(),
                user_id=str(bot.self_id),
                group_id=data.get("group_id"),
                guild_id=data.get("guild_id"),
                channel_id=data.get("channel_id"),
            )

            async with create_session() as session:
                session.add(record)
                await session.commit()

    class Serializer(MessageSerializer[Message]):
        pass

    class Deserializer(MessageDeserializer[Message]):
        @classmethod
        @overrides(MessageDeserializer)
        def get_message_class(cls) -> Type[Message]:
            return Message

    adapter = SupportedAdapter.onebot_v12
    register_serializer(adapter, Serializer)
    register_deserializer(adapter, Deserializer)

except ImportError:
    pass
