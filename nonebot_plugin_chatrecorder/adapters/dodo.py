from datetime import datetime, timezone
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
    from nonebot.adapters.dodo import Bot, Message, MessageEvent
    from nonebot.adapters.dodo.models import MessageReturn

    adapter = SupportAdapter.dodo

    @event_postprocessor
    async def record_recv_msg(event: MessageEvent, session: Uninfo):
        session_persist_id = await get_session_persist_id(session)

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=remove_timezone(event.timestamp),
            type=record_type(event),
            message_id=event.message_id,
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
            if e or not result or not isinstance(result, MessageReturn):
                return

            if api == "set_channel_message_send":
                scene_type = SceneType.CHANNEL_TEXT
                scene_id = data["channel_id"]
                parent = None
            elif api == "set_personal_message_send":
                scene_type = SceneType.PRIVATE
                scene_id = data["dodo_source_id"]
                parent = Scene(id=data["island_source_id"], type=SceneType.GUILD)
            else:
                return

            message = Message.from_message_body(data["message_body"])

            session = Session(
                self_id=bot.self_id,
                adapter=adapter,
                scope=SupportScope.dodo,
                scene=Scene(id=scene_id, type=scene_type, parent=parent),
                user=User(id=bot.self_id),
            )
            session_persist_id = await get_session_persist_id(session)

            record = MessageRecord(
                session_persist_id=session_persist_id,
                time=remove_timezone(datetime.now(timezone.utc)),
                type="message_sent",
                message_id=result.message_id,
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
