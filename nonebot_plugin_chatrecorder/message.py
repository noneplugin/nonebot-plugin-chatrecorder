import abc
from typing import Any, Dict, Generic, List, Type, TypeVar, Union

from nonebot.adapters import Bot, Message
from pydantic import parse_obj_as

from .consts import SupportedAdapter
from .exception import AdapterNotInstalled, AdapterNotSupported

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


def get_adapter_type(bot_type: str) -> SupportedAdapter:
    for adapter in SupportedAdapter:
        if bot_type == adapter.value:
            return adapter

    raise AdapterNotSupported(bot_type)


def get_serializer(adapter: SupportedAdapter) -> Type[MessageSerializer]:
    if adapter not in _serializers:
        raise AdapterNotInstalled(adapter.value)
    return _serializers[adapter]


def get_deserializer(adapter: SupportedAdapter) -> Type[MessageDeserializer]:
    if adapter not in _deserializers:
        raise AdapterNotInstalled(adapter.value)
    return _deserializers[adapter]


def register_serializer(adapter: SupportedAdapter, serializer: Type[MessageSerializer]):
    _serializers[adapter] = serializer


def register_deserializer(
    adapter: SupportedAdapter, deserializer: Type[MessageDeserializer]
):
    _deserializers[adapter] = deserializer


def serialize_message(
    bot_type: Union[Bot, SupportedAdapter, str], msg: Message
) -> JsonMsg:
    if isinstance(bot_type, Bot):
        bot_type = bot_type.type
    if isinstance(bot_type, str):
        bot_type = get_adapter_type(bot_type)
    return get_serializer(bot_type).serialize(msg)


def deserialize_message(
    bot_type: Union[Bot, SupportedAdapter, str], msg: JsonMsg
) -> Message:
    if isinstance(bot_type, Bot):
        bot_type = bot_type.type
    if isinstance(bot_type, str):
        bot_type = get_adapter_type(bot_type)
    return get_deserializer(bot_type).deserialize(msg)
