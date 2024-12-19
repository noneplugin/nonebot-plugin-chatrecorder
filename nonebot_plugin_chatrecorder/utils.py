from datetime import datetime, timezone
from typing import Union

from nonebot.adapters import Event
from nonebot_plugin_uninfo import SceneType, SupportAdapter, SupportScope


def remove_timezone(dt: datetime) -> datetime:
    """移除时区"""
    if dt.tzinfo is None:
        return dt
    # 先转至 UTC 时间，再移除时区
    dt = dt.astimezone(timezone.utc)
    return dt.replace(tzinfo=None)


def is_fake_event(event: Event) -> bool:
    return hasattr(event, "_is_fake") and event._is_fake()  # type: ignore


def record_type(event: Event) -> str:
    return "fake" if is_fake_event(event) else "message"


def scene_type_value(scene_type: Union[int, SceneType]) -> int:
    return scene_type.value if isinstance(scene_type, SceneType) else scene_type


def adapter_value(adapter: Union[str, SupportAdapter]) -> str:
    return adapter.value if isinstance(adapter, SupportAdapter) else adapter


def scope_value(scope: Union[str, SupportScope]) -> str:
    return scope.value if isinstance(scope, SupportScope) else scope
