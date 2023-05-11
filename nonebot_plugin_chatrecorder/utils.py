from nonebot.adapters import Bot

from .consts import SupportedAdapter
from .exception import AdapterNotSupported


def extract_adapter_type(bot: Bot) -> SupportedAdapter:
    adapter_name = bot.adapter.get_name()
    for adapter in SupportedAdapter:
        if adapter_name == adapter.value:
            return adapter

    raise AdapterNotSupported(adapter_name)
