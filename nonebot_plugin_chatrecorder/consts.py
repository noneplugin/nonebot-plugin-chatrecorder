from nonebot_plugin_localstore import get_cache_dir
from strenum import StrEnum

CACHE_DIR = get_cache_dir("nonebot_plugin_chatrecorder")
IMAGE_CACHE_DIR = CACHE_DIR / "images"
RECORD_CACHE_DIR = CACHE_DIR / "records"
VIDEO_CACHE_DIR = CACHE_DIR / "videos"

IMAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
RECORD_CACHE_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_CACHE_DIR.mkdir(parents=True, exist_ok=True)


class SupportedAdapter(StrEnum):
    console = "Console"
    discord = "Discord"
    dodo = "DoDo"
    feishu = "Feishu"
    kaiheila = "Kaiheila"
    onebot_v11 = "OneBot V11"
    onebot_v12 = "OneBot V12"
    qq = "QQ"
    red = "RedProtocol"
    satori = "Satori"
    telegram = "Telegram"


class SupportedPlatform(StrEnum):
    console = "console"
    discord = "discord"
    dodo = "dodo"
    feishu = "feishu"
    kaiheila = "kaiheila"
    qq = "qq"
    qqguild = "qqguild"
    telegram = "telegram"
    unknown = "unknown"
