from datetime import datetime, timezone
from typing import Any, Optional, Union

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
    from nonebot.adapters.qq import Bot, GuildMessageEvent, Message, QQMessageEvent
    from nonebot.adapters.qq.models import Message as GuildMessage
    from nonebot.adapters.qq.models import (
        PostC2CMessagesReturn,
        PostGroupMessagesReturn,
    )

    adapter = SupportAdapter.qq

    @event_postprocessor
    async def record_recv_msg(
        event: Union[GuildMessageEvent, QQMessageEvent], session: Uninfo
    ):
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

            parent = None

            if api == "post_messages":
                assert isinstance(result, GuildMessage)
                scene_type = SceneType.CHANNEL_TEXT
                scene_id = result.channel_id
                parent = Scene(id=result.guild_id, type=SceneType.GUILD)
                scope = SupportScope.qq_guild

            elif api == "post_dms_messages":
                assert isinstance(result, GuildMessage)
                scene_type = SceneType.PRIVATE
                scene_id = result.channel_id
                parent = Scene(id=result.guild_id, type=SceneType.GUILD)
                scope = SupportScope.qq_guild

            elif api == "post_c2c_messages":
                assert isinstance(result, PostC2CMessagesReturn)
                scene_type = SceneType.PRIVATE
                scene_id = data["openid"]
                scope = SupportScope.qq_api

            elif api == "post_group_messages":
                assert isinstance(result, PostGroupMessagesReturn)
                scene_type = SceneType.GROUP
                scene_id = data["group_openid"]
                scope = SupportScope.qq_api

            session = Session(
                self_id=bot.self_id,
                adapter=adapter,
                scope=scope,
                scene=Scene(id=scene_id, type=scene_type, parent=parent),
                user=User(id=bot.self_id),
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
