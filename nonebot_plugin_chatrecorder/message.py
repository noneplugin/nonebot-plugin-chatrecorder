import abc
from typing import Any, Dict, Generic, List, Type, TypeVar

from nonebot.adapters import Bot, Message
from pydantic import parse_obj_as

from .consts import SupportedAdapter
from .exception import AdapterNotInstalled
from .utils import extract_adapter_type

JsonMsg = List[Dict[str, Any]]
TM = TypeVar("TM", bound="Message")


class MessageSerializer(abc.ABC, Generic[TM]):
    @classmethod
    def serialize(cls, msg: TM) -> JsonMsg:
        return [seg.__dict__ for seg in msg]


class MessageDeserializer(abc.ABC, Generic[TM]):
    @classmethod
    @abc.abstractmethod
    def get_message_class(cls) -> Type[TM]:
        raise NotImplementedError

    @classmethod
    def deserialize(cls, msg: JsonMsg) -> TM:
        return parse_obj_as(cls.get_message_class(), msg)


_serializers: Dict[SupportedAdapter, Type[MessageSerializer]] = {}
_deserializers: Dict[SupportedAdapter, Type[MessageDeserializer]] = {}


def get_serializer(bot: Bot) -> Type[MessageSerializer]:
    adapter = extract_adapter_type(bot)
    if adapter not in _serializers:
        raise AdapterNotInstalled(adapter.value)
    return _serializers[adapter]


def get_deserializer(bot: Bot) -> Type[MessageDeserializer]:
    adapter = extract_adapter_type(bot)
    if adapter not in _deserializers:
        raise AdapterNotInstalled(adapter.value)
    return _deserializers[adapter]


def register_serializer(adapter: SupportedAdapter, serializer: Type[MessageSerializer]):
    _serializers[adapter] = serializer


def register_deserializer(
    adapter: SupportedAdapter, deserializer: Type[MessageDeserializer]
):
    _deserializers[adapter] = deserializer


def serialize_message(bot: Bot, msg: Message) -> JsonMsg:
    return get_serializer(bot).serialize(msg)


def deserialize_message(bot: Bot, msg: JsonMsg) -> Message:
    return get_deserializer(bot).deserialize(msg)
