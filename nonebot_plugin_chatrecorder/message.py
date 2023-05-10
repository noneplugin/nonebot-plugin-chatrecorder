import base64
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Type, TypeVar

from nonebot.adapters import Message
from nonebot_plugin_datastore import get_plugin_data
from pydantic import parse_obj_as

cache_dir = get_plugin_data().cache_dir
for dir_name in ("images", "records", "videos"):
    (cache_dir / dir_name).mkdir(exist_ok=True)


JsonMsg = List[Dict[str, Any]]
TM = TypeVar("TM", bound="Message")


def serialize_message(msg: Message) -> JsonMsg:
    try:
        if isinstance(msg, V11Msg):
            cache_b64_msg_v11(msg)
    except NameError:
        pass

    return [seg.__dict__ for seg in msg]


def deserialize_message(msg: JsonMsg, msg_class: Type[TM]) -> TM:
    return parse_obj_as(msg_class, msg)


try:
    from nonebot.adapters.onebot.v11 import Message as V11Msg
    from nonebot.adapters.onebot.v11 import MessageSegment as V11MsgSeg

    def cache_b64_msg_v11(msg: V11Msg):
        for seg in msg:
            if seg.type == "image":
                cache_b64_msg_seg(seg, "images")
            elif seg.type == "record":
                cache_b64_msg_seg(seg, "records")
            elif seg.type == "video":
                cache_b64_msg_seg(seg, "videos")

    def cache_b64_msg_seg(seg: V11MsgSeg, dir_name: str):
        def replace_seg_file(path: Path):
            seg.data["file"] = f"file:///{path.resolve()}"

        file = seg.data.get("file", "")
        if not file or not file.startswith("base64://"):
            return

        cache_file_dir = cache_dir / dir_name
        data = base64.b64decode(file.replace("base64://", ""))
        hash = hashlib.md5(data).hexdigest()
        filename = f"{hash}.cache"
        cache_file_path = cache_file_dir / filename
        cache_files = [f.name for f in cache_file_dir.iterdir() if f.is_file()]
        if filename in cache_files:
            replace_seg_file(cache_file_path)
        else:
            with cache_file_path.open("wb") as f:
                f.write(data)
            replace_seg_file(cache_file_path)

except ImportError:
    pass
