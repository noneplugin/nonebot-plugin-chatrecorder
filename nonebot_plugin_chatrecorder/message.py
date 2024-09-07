import abc
from typing import Any, Generic, TypeVar, Union

from nonebot.adapters import Bot, Message
from nonebot.compat import type_validate_python

from .consts import SupportedAdapter
from .exception import AdapterNotInstalled, AdapterNotSupported

JsonMsg = list[dict[str, Any]]
TM = TypeVar("TM", bound="Message")


class MessageSerializer(abc.ABC, Generic[TM]):
    @classmethod
    def serialize(cls, msg: TM) -> JsonMsg:
        return [seg.__dict__ for seg in msg]


class MessageDeserializer(abc.ABC, Generic[TM]):
    @classmethod
    @abc.abstractmethod
    def get_message_class(cls) -> type[TM]:
        raise NotImplementedError

    @classmethod
    def deserialize(cls, msg: JsonMsg) -> TM:
        return type_validate_python(cls.get_message_class(), msg)


_serializers: dict[SupportedAdapter, type[MessageSerializer]] = {}
_deserializers: dict[SupportedAdapter, type[MessageDeserializer]] = {}


def get_adapter_type(bot_type: str) -> SupportedAdapter:
    for adapter in SupportedAdapter:
        if bot_type == adapter.value:
            return adapter

    raise AdapterNotSupported(bot_type)


def get_serializer(adapter: SupportedAdapter) -> type[MessageSerializer]:
    if adapter not in _serializers:
        raise AdapterNotInstalled(adapter.value)
    return _serializers[adapter]


def get_deserializer(adapter: SupportedAdapter) -> type[MessageDeserializer]:
    if adapter not in _deserializers:
        raise AdapterNotInstalled(adapter.value)
    return _deserializers[adapter]


def register_serializer(adapter: SupportedAdapter, serializer: type[MessageSerializer]):
    _serializers[adapter] = serializer


def register_deserializer(
    adapter: SupportedAdapter, deserializer: type[MessageDeserializer]
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
