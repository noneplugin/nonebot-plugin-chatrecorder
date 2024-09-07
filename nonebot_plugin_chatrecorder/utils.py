from datetime import datetime, timezone

from nonebot.adapters import Event

from .consts import SupportedPlatform


def remove_timezone(dt: datetime) -> datetime:
    """移除时区"""
    if dt.tzinfo is None:
        return dt
    # 先转至 UTC 时间，再移除时区
    dt = dt.astimezone(timezone.utc)
    return dt.replace(tzinfo=None)


def format_platform(platform: str) -> str:
    if platform in ("onebot", "red", "chronocat"):
        return SupportedPlatform.qq
    elif platform in ("kook",):
        return SupportedPlatform.kaiheila
    elif platform not in list(SupportedPlatform):
        return SupportedPlatform.unknown
    return platform


def is_fake_event(event: Event) -> bool:
    return hasattr(event, "_is_fake") and event._is_fake()  # type: ignore


def record_type(event: Event) -> str:
    return "fake" if is_fake_event(event) else "message"
