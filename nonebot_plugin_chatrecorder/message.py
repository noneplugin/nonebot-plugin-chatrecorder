import abc
from typing import Any, Generic, TypeVar, Union

from nonebot.adapters import Bot, Message
from nonebot.compat import type_validate_python
from nonebot_plugin_uninfo import SupportAdapter

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


_serializers: dict[SupportAdapter, type[MessageSerializer]] = {}
_deserializers: dict[SupportAdapter, type[MessageDeserializer]] = {}


def get_adapter_type(bot_type: str) -> SupportAdapter:
    for adapter in SupportAdapter:
        if bot_type == adapter.value:
            return adapter

    raise AdapterNotSupported(bot_type)


def get_serializer(adapter: SupportAdapter) -> type[MessageSerializer]:
    if adapter not in _serializers:
        raise AdapterNotInstalled(adapter.value)
    return _serializers[adapter]


def get_deserializer(adapter: SupportAdapter) -> type[MessageDeserializer]:
    if adapter not in _deserializers:
        raise AdapterNotInstalled(adapter.value)
    return _deserializers[adapter]


def register_serializer(adapter: SupportAdapter, serializer: type[MessageSerializer]):
    _serializers[adapter] = serializer


def register_deserializer(
    adapter: SupportAdapter, deserializer: type[MessageDeserializer]
):
    _deserializers[adapter] = deserializer


def serialize_message(
    bot_type: Union[Bot, SupportAdapter, str], msg: Message
) -> JsonMsg:
    if isinstance(bot_type, Bot):
        bot_type = bot_type.type
    if isinstance(bot_type, str):
        bot_type = get_adapter_type(bot_type)
    return get_serializer(bot_type).serialize(msg)


def deserialize_message(
    bot_type: Union[Bot, SupportAdapter, str], msg: JsonMsg
) -> Message:
    if isinstance(bot_type, Bot):
        bot_type = bot_type.type
    if isinstance(bot_type, str):
        bot_type = get_adapter_type(bot_type)
    return get_deserializer(bot_type).deserialize(msg)
