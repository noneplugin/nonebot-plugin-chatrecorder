from datetime import datetime, timezone
from typing import Any, Optional, Union

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
    from nonebot.adapters.qq import Bot, GuildMessageEvent, Message, QQMessageEvent
    from nonebot.adapters.qq.models import Message as GuildMessage
    from nonebot.adapters.qq.models import (
        PostC2CMessagesReturn,
        PostGroupMessagesReturn,
    )

    adapter = SupportedAdapter.qq

    @event_postprocessor
    async def record_recv_msg(
        bot: Bot, event: Union[GuildMessageEvent, QQMessageEvent]
    ):
        session = extract_session(bot, event)
        session_persist_id = await get_session_persist_id(session)

        if isinstance(event, QQMessageEvent):
            if isinstance(event.timestamp, str):
                time = datetime.fromisoformat(event.timestamp)
            else:
                time = event.timestamp
        else:
            if event.timestamp:
                time = event.timestamp
            else:
                time = datetime.now(timezone.utc)
        time = remove_timezone(time)

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=time,
            type=record_type(event),
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
            data: dict[str, Any],
            result: Any,
        ):
            if not isinstance(bot, Bot):
                return
            if e or not result:
                return
            if api not in (
                "post_messages",
                "post_dms_messages",
                "post_c2c_messages",
                "post_group_messages",
            ):
                return

            id1 = None
            id2 = None
            id3 = None
            level = SessionLevel.LEVEL0
            platform = SupportedPlatform.qqguild

            if api == "post_messages":
                assert isinstance(result, GuildMessage)
                level = SessionLevel.LEVEL3
                id3 = result.guild_id
                id2 = result.channel_id

            elif api == "post_dms_messages":
                assert isinstance(result, GuildMessage)
                level = SessionLevel.LEVEL1
                id3 = data["guild_id"]

            elif api == "post_c2c_messages":
                assert isinstance(result, PostC2CMessagesReturn)
                level = SessionLevel.LEVEL1
                id1 = data["openid"]
                platform = SupportedPlatform.qq

            elif api == "post_group_messages":
                assert isinstance(result, PostGroupMessagesReturn)
                level = SessionLevel.LEVEL2
                id2 = data["group_openid"]
                platform = SupportedPlatform.qq

            session = Session(
                bot_id=bot.self_id,
                bot_type=bot.type,
                platform=platform,
                level=level,
                id1=id1,
                id2=id2,
                id3=id3,
            )
            session_persist_id = await get_session_persist_id(session)

            assert result.id
            time = result.timestamp if result.timestamp else datetime.now(timezone.utc)
            time = remove_timezone(time)
            message = (
                Message.from_guild_message(result)
                if isinstance(result, GuildMessage)
                else Message(data.get("content"))
            )

            record = MessageRecord(
                session_persist_id=session_persist_id,
                time=time,
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
        def get_message_class(cls) -> type[Message]:
            return Message

    register_serializer(adapter, Serializer)
    register_deserializer(adapter, Deserializer)

except ImportError:
    pass
