from datetime import datetime, timezone
from typing import Any, Optional, cast

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
    from nonebot.adapters.satori import Bot, Message
    from nonebot.adapters.satori.event import MessageCreatedEvent
    from nonebot.adapters.satori.models import MessageObject
    from nonebot_plugin_uninfo.adapters.satori.main import TYPE_MAPPING

    adapter = SupportAdapter.satori

    @event_postprocessor
    async def record_recv_msg(event: MessageCreatedEvent, session: Uninfo):
        session_persist_id = await get_session_persist_id(session)

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=remove_timezone(event.timestamp.astimezone(timezone.utc)),
            type=record_type(event),
            message_id=event.message.id,
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
            if e or not result or not isinstance(result, list):
                return
            if api not in ["message_create"]:
                return
            for res in result:
                if not isinstance(res, MessageObject):
                    return
            result_messages = cast(list[MessageObject], result)
            result_message = result_messages[0]

            parent = None

            if result_message.guild and result_message.channel:
                scene_type = TYPE_MAPPING[result_message.channel.type]
                scene_id = result_message.channel.id
                parent = Scene(id=result_message.guild.id, type=SceneType.GUILD)
                if (
                    "guild.plain" in bot._self_info.features
                    or result_message.guild.id == result_message.channel.id
                ):
                    scene_type = SceneType.GROUP
                    parent.type = SceneType.GROUP

            elif result_message.guild:
                scene_type = (
                    SceneType.GROUP
                    if "guild.plain" in bot._self_info.features
                    else SceneType.GUILD
                )
                scene_id = result_message.guild.id

            elif result_message.channel:
                scene_type = (
                    SceneType.GROUP
                    if "guild.plain" in bot._self_info.features
                    else SceneType.GUILD
                )
                scene_id = result_message.channel.id

            else:
                return

            session = Session(
                self_id=bot.self_id,
                adapter=adapter,
                scope=SupportScope.ensure_satori(bot.platform),
                scene=Scene(id=scene_id, type=scene_type, parent=parent),
                user=User(id=bot.self_id),
            )
            session_persist_id = await get_session_persist_id(session)

            message_id = "_".join([msg.id for msg in result_messages])
            message = Message()
            for msg in result_messages:
                message += Message(msg.content)
            message_time = (
                result_message.created_at.astimezone(timezone.utc)
                if result_message.created_at
                else datetime.now(timezone.utc)
            )
            message_time = remove_timezone(message_time)

            record = MessageRecord(
                session_persist_id=session_persist_id,
                time=message_time,
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
        def get_message_class(cls) -> type[Message]:
            return Message

    register_serializer(adapter, Serializer)
    register_deserializer(adapter, Deserializer)

except ImportError:
    pass
