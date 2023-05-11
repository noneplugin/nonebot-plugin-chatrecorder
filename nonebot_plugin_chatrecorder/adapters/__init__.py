from enum import Enum

from nonebot.adapters import Bot

from . import onebot_v11, onebot_v12
from .consts import SupportedAdapter
from .exception import AdapterNotSupported
from .message import deserialize_message, serialize_message
from .utils import extract_adapter_type
