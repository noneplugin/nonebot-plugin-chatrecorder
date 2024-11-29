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
    from nonebot.adapters.onebot.v12 import Bot, Message, MessageEvent

    adapter = SupportAdapter.onebot12

    @event_postprocessor
    async def record_recv_msg(event: MessageEvent, session: Uninfo):
        session_persist_id = await get_session_persist_id(session)

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=remove_timezone(event.time),
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
            if e or not result:
                return
            if api not in ["send_message"]:
                return

            parent = None
            detail_type = data["detail_type"]
            if detail_type == "channel":
                scene_type = SceneType.CHANNEL_TEXT
                scene_id = data["channel_id"]
                parent = (
                    Scene(id=data["guild_id"], type=SceneType.GUILD)
                    if data.get("guild_id")
                    else None
                )
            elif detail_type == "group":
                scene_type = SceneType.GROUP
                scene_id = data["group_id"]
            elif detail_type == "private":
                scene_type = SceneType.PRIVATE
                scene_id = data["user_id"]
            else:
                return

            session = Session(
                self_id=bot.self_id,
                adapter=adapter,
                scope=SupportScope.ensure_ob12(bot.platform),
                scene=Scene(id=scene_id, type=scene_type, parent=parent),
                user=User(id=bot.self_id),
            )
            session_persist_id = await get_session_persist_id(session)

            message = Message(data["message"])
            record = MessageRecord(
                session_persist_id=session_persist_id,
                time=remove_timezone(
                    datetime.fromtimestamp(result["time"], timezone.utc)
                ),
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
        def get_message_class(cls) -> type[Message]:
            return Message

    register_serializer(adapter, Serializer)
    register_deserializer(adapter, Deserializer)

except ImportError:
    pass
