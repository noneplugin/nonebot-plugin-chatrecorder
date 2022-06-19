import json
import base64
import hashlib
from pathlib import Path
from pydantic import parse_obj_as
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot_plugin_datastore import PluginData

cache_dir = PluginData("chatrecorder").cache_dir
for dir_name in ("images", "records", "videos"):
    (cache_dir / dir_name).mkdir(exist_ok=True)


def serialize_message(msg: Message) -> str:
    cache_file(msg)
    return json.dumps(
        [{"type": seg.type, "data": seg.data} for seg in msg],
        ensure_ascii=False,
    )


def deserialize_message(msg: str) -> Message:
    return parse_obj_as(Message, json.loads(msg))


def cache_file(msg: Message):
    for seg in msg:
        if seg.type == "image":
            cache_b64_file(seg, "images")
        elif seg.type == "record":
            cache_b64_file(seg, "records")
        elif seg.type == "video":
            cache_b64_file(seg, "videos")


def cache_b64_file(seg: MessageSegment, dir_name: str):
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
        with cache_file_path.open('wb') as f:
            f.write(data)
        replace_seg_file(cache_file_path)
