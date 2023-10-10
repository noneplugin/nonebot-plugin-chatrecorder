import base64
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Type

from nonebot.adapters import Bot as BaseBot
from nonebot.message import event_postprocessor
from nonebot_plugin_orm import get_session
from nonebot_plugin_session import Session, SessionLevel, extract_session
from nonebot_plugin_session_orm import get_session_persist_id
from typing_extensions import override

from ..config import plugin_config
from ..consts import (
    IMAGE_CACHE_DIR,
    RECORD_CACHE_DIR,
    VIDEO_CACHE_DIR,
    SupportedAdapter,
    SupportedPlatform,
)
from ..message import (
    JsonMsg,
    MessageDeserializer,
    MessageSerializer,
    register_deserializer,
    register_serializer,
    serialize_message,
)
from ..model import MessageRecord

try:
    from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, MessageSegment

    adapter = SupportedAdapter.onebot_v11

    @event_postprocessor
    async def record_recv_msg(bot: Bot, event: MessageEvent):
        session = extract_session(bot, event)
        session_persist_id = await get_session_persist_id(session)

        record = MessageRecord(
            session_persist_id=session_persist_id,
            time=datetime.utcfromtimestamp(event.time),
            type=event.post_type,
            message_id=str(event.message_id),
            message=serialize_message(adapter, event.message),
            plain_text=event.message.extract_plain_text(),
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
            result: Optional[Dict[str, Any]],
        ):
            if not isinstance(bot, Bot):
                return
            if e or not result:
                return
            if api not in ["send_msg", "send_private_msg", "send_group_msg"]:
                return

            if api == "send_group_msg" or (
                api == "send_msg"
                and (
                    data.get("message_type") == "group"
                    or (data.get("message_type") == None and data.get("group_id"))
                )
            ):
                level = SessionLevel.LEVEL2
            else:
                level = SessionLevel.LEVEL1

            session = Session(
                bot_id=bot.self_id,
                bot_type=bot.type,
                platform=SupportedPlatform.qq,
                level=level,
                id1=str(data.get("user_id", "")) or None,
                id2=str(data.get("group_id", "")) or None,
                id3=None,
            )
            session_persist_id = await get_session_persist_id(session)

            message = Message(data["message"])
            record = MessageRecord(
                session_persist_id=session_persist_id,
                time=datetime.utcnow(),
                type="message_sent",
                message_id=str(result["message_id"]),
                message=serialize_message(adapter, message),
                plain_text=message.extract_plain_text(),
            )
            async with get_session() as db_session:
                db_session.add(record)
                await db_session.commit()

    def cache_b64_msg(msg: Message):
        for seg in msg:
            if seg.type == "image":
                cache_b64_msg_seg(seg, IMAGE_CACHE_DIR)
            elif seg.type == "record":
                cache_b64_msg_seg(seg, RECORD_CACHE_DIR)
            elif seg.type == "video":
                cache_b64_msg_seg(seg, VIDEO_CACHE_DIR)

    def cache_b64_msg_seg(seg: MessageSegment, cache_dir: Path):
        def replace_seg_file(path: Path):
            seg.data["file"] = f"file:///{path.resolve()}"

        file = seg.data.get("file", "")
        if not file or not file.startswith("base64://"):
            return

        data = base64.b64decode(file.replace("base64://", ""))
        hash = hashlib.md5(data).hexdigest()
        filename = f"{hash}.cache"
        cache_file_path = cache_dir / filename
        cache_files = [f.name for f in cache_dir.iterdir() if f.is_file()]
        if filename in cache_files:
            replace_seg_file(cache_file_path)
        else:
            with cache_file_path.open("wb") as f:
                f.write(data)
            replace_seg_file(cache_file_path)

    class Serializer(MessageSerializer[Message]):
        @classmethod
        @override
        def serialize(cls, msg: Message) -> JsonMsg:
            cache_b64_msg(msg)
            return super().serialize(msg)

    class Deserializer(MessageDeserializer[Message]):
        @classmethod
        @override
        def get_message_class(cls) -> Type[Message]:
            return Message

    register_serializer(adapter, Serializer)
    register_deserializer(adapter, Deserializer)

except ImportError:
    pass
