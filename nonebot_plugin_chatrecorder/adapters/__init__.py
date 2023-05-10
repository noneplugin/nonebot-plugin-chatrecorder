from enum import Enum
from typing import Type

from nonebot.adapters import Message

from ..exception import AdapterNotInstalled, AdapterNotSupported
from . import onebot_v11, onebot_v12


class SupportedAdapters(Enum):
    onebot_v11 = "OneBot V11"
    onebot_v12 = "OneBot V12"


def get_message_class_by_adapter_name(adapter_name: str) -> Type[Message]:
    if adapter_name == SupportedAdapters.onebot_v11.value:
        try:
            from nonebot.adapters.onebot.v11 import Message as V11Msg

            return V11Msg
        except ImportError:
            raise AdapterNotInstalled(adapter_name)

    if adapter_name == SupportedAdapters.onebot_v12.value:
        try:
            from nonebot.adapters.onebot.v12 import Message as V12Msg

            return V12Msg
        except ImportError:
            raise AdapterNotInstalled(adapter_name)

    raise AdapterNotSupported(adapter_name)
