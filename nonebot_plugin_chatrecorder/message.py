import json
from nonebot.adapters.onebot.v11 import Message


def serialize_message(msg: Message) -> str:
    return json.dumps(
        [{"type": seg.type, "data": seg.data} for seg in msg],
        ensure_ascii=False,
    )


def deserialize_message(msg: str) -> Message:
    return Message(json.loads(msg))
