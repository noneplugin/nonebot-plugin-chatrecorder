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
    from nonebot.adapters.kaiheila import Bot, Message, MessageSegment
    from nonebot.adapters.kaiheila.api.model import MessageCreateReturn
    from nonebot.adapters.kaiheila.event import MessageEvent

    adapter = SupportAdapter.kook

    @event_postprocessor
    async def record_recv_msg(event: MessageEvent, session: Uninfo):
        session_persist_id = await get_session_persist_id(session)

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=remove_timezone(
                datetime.fromtimestamp(event.msg_timestamp / 1000, timezone.utc)
            ),
            type=record_type(event),
            message_id=event.msg_id,
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
            if not (
                isinstance(result, MessageCreateReturn)
                and result.msg_id
                and result.msg_timestamp
            ):
                return

            scene_id = data["target_id"]
            if api == "message_create":
                scene_type = SceneType.CHANNEL_TEXT
            elif api == "directMessage_create":
                scene_type = SceneType.PRIVATE
            else:
                return

            type_code = data["type"]
            content = data["content"]
            if type_code == 1:
                message = MessageSegment.text(content)
            elif type_code == 2:
                message = MessageSegment.image(content)
            elif type_code == 3:
                message = MessageSegment.video(content)
            elif type_code == 4:
                message = MessageSegment.file(content)
            elif type_code == 8:
                message = MessageSegment.audio(content)
            elif type_code == 9:
                message = MessageSegment.KMarkdown(content)
            elif type_code == 10:
                message = MessageSegment.Card(content)
            else:
                message = content
            message = Message(message)

            session = Session(
                self_id=bot.self_id,
                adapter=adapter,
                scope=SupportScope.kook,
                scene=Scene(id=scene_id, type=scene_type),
                user=User(id=bot.self_id),
            )
            session_persist_id = await get_session_persist_id(session)

            record = MessageRecord(
                session_persist_id=session_persist_id,
                time=remove_timezone(
                    datetime.fromtimestamp(result.msg_timestamp / 1000, timezone.utc)
                ),
                type="message_sent",
                message_id=result.msg_id,
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
