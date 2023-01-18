import json
import base64
import hashlib
from pathlib import Path
from pydantic import parse_obj_as
from typing import Union, Type, overload

from nonebot.utils import DataclassEncoder

from nonebot.adapters.onebot.v11 import Message as V11Msg
from nonebot.adapters.onebot.v11 import MessageSegment as V11MsgSeg

from nonebot.adapters.onebot.v12 import Message as V12Msg

from nonebot_plugin_datastore import get_plugin_data


cache_dir = get_plugin_data().cache_dir
for dir_name in ("images", "records", "videos"):
    (cache_dir / dir_name).mkdir(exist_ok=True)


def serialize_message(msg: Union[V11Msg, V12Msg]) -> str:
    if isinstance(msg, V11Msg):
        cache_file(msg)
    return DataclassEncoder(ensure_ascii=False).encode(msg)


@overload
def deserialize_message(msg: str, msg_class: Type[V11Msg]) -> V11Msg:
    ...


@overload
def deserialize_message(msg: str, msg_class: Type[V12Msg]) -> V12Msg:
    ...


def deserialize_message(
    msg: str, msg_class: Union[Type[V11Msg], Type[V12Msg]]
) -> Union[V11Msg, V12Msg]:
    return parse_obj_as(msg_class, json.loads(msg))


def cache_file(msg: V11Msg):
    for seg in msg:
        if seg.type == "image":
            cache_b64_file(seg, "images")
        elif seg.type == "record":
            cache_b64_file(seg, "records")
        elif seg.type == "video":
            cache_b64_file(seg, "videos")


def cache_b64_file(seg: V11MsgSeg, dir_name: str):
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
