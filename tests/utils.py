import sys
from datetime import datetime
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GMEvent
    from nonebot.adapters.onebot.v11 import PrivateMessageEvent as V11PMEvent
    from nonebot.adapters.onebot.v12 import ChannelMessageEvent as V12CMEvent
    from nonebot.adapters.onebot.v12 import GroupMessageEvent as V12GMEvent
    from nonebot.adapters.onebot.v12 import PrivateMessageEvent as V12PMEvent


def fake_group_message_event_v11(**field) -> "V11GMEvent":
    from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GMEvent
    from nonebot.adapters.onebot.v11 import Message as V11Msg
    from nonebot.adapters.onebot.v11.event import Sender
    from pydantic import create_model

    _Fake = create_model("_Fake", __base__=V11GMEvent)

    class FakeEvent(_Fake):
        time: int = 1000000
        self_id: int = 11
        post_type: Literal["message"] = "message"
        sub_type: str = "normal"
        user_id: int = 10
        message_type: Literal["group"] = "group"
        group_id: int = 10000
        message_id: int = 1
        message: V11Msg = V11Msg("test")
        original_message: V11Msg = V11Msg("test")
        raw_message: str = "test"
        font: int = 0
        sender: Sender = Sender(
            card="",
            nickname="test",
            role="member",
        )
        to_me: bool = False

        class Config:
            extra = "forbid"

    return FakeEvent(**field)


def fake_private_message_event_v11(**field) -> "V11PMEvent":
    from nonebot.adapters.onebot.v11 import Message as V11Msg
    from nonebot.adapters.onebot.v11 import PrivateMessageEvent as V11PMEvent
    from nonebot.adapters.onebot.v11.event import Sender
    from pydantic import create_model

    _Fake = create_model("_Fake", __base__=V11PMEvent)

    class FakeEvent(_Fake):
        time: int = 1000000
        self_id: int = 11
        post_type: Literal["message"] = "message"
        sub_type: str = "friend"
        user_id: int = 10
        message_type: Literal["private"] = "private"
        message_id: int = 1
        message: V11Msg = V11Msg("test")
        original_message: V11Msg = V11Msg("test")
        raw_message: str = "test"
        font: int = 0
        sender: Sender = Sender(nickname="test")
        to_me: bool = False

        class Config:
            extra = "forbid"

    return FakeEvent(**field)


def fake_group_message_event_v12(**field) -> "V12GMEvent":
    from nonebot.adapters.onebot.v12 import GroupMessageEvent as V12GMEvent
    from nonebot.adapters.onebot.v12 import Message as V12Msg
    from nonebot.adapters.onebot.v12.event import BotSelf
    from pydantic import create_model

    _Fake = create_model("_Fake", __base__=V12GMEvent)

    class FakeEvent(_Fake):
        self: BotSelf = BotSelf(platform="qq", user_id="1")
        id: str = "12"
        time: datetime = datetime.fromtimestamp(1000000)
        type: Literal["message"] = "message"
        detail_type: Literal["group"] = "group"
        sub_type: str = ""
        message_id: str = "10"
        message: V12Msg = V12Msg("test")
        original_message: V12Msg = V12Msg("test")
        alt_message: str = "test"
        user_id: str = "100"
        group_id: str = "10000"
        to_me: bool = False

        class Config:
            extra = "forbid"

    return FakeEvent(**field)


def fake_private_message_event_v12(**field) -> "V12PMEvent":
    from nonebot.adapters.onebot.v12 import Message as V12Msg
    from nonebot.adapters.onebot.v12 import PrivateMessageEvent as V12PMEvent
    from nonebot.adapters.onebot.v12.event import BotSelf
    from pydantic import create_model

    _Fake = create_model("_Fake", __base__=V12PMEvent)

    class FakeEvent(_Fake):
        self: BotSelf = BotSelf(platform="qq", user_id="1")
        id: str = "12"
        time: datetime = datetime.fromtimestamp(1000000)
        type: Literal["message"] = "message"
        detail_type: Literal["private"] = "private"
        sub_type: str = ""
        message_id: str = "10"
        message: V12Msg = V12Msg("test")
        original_message: V12Msg = V12Msg("test")
        alt_message: str = "test"
        user_id: str = "100"
        to_me: bool = False

        class Config:
            extra = "forbid"

    return FakeEvent(**field)


def fake_channel_message_event_v12(**field) -> "V12CMEvent":
    from nonebot.adapters.onebot.v12 import ChannelMessageEvent as V12CMEvent
    from nonebot.adapters.onebot.v12 import Message as V12Msg
    from nonebot.adapters.onebot.v12.event import BotSelf
    from pydantic import create_model

    _Fake = create_model("_Fake", __base__=V12CMEvent)

    class FakeEvent(_Fake):
        self: BotSelf = BotSelf(platform="qq", user_id="1")
        id: str = "12"
        time: datetime = datetime.fromtimestamp(1000000)
        type: Literal["message"] = "message"
        detail_type: Literal["channel"] = "channel"
        sub_type: str = ""
        message_id: str = "10"
        message: V12Msg = V12Msg("test")
        original_message: V12Msg = V12Msg("test")
        alt_message: str = "test"
        user_id: str = "100"
        guild_id: str = "10000"
        channel_id: str = "100000"
        to_me: bool = False

        class Config:
            extra = "forbid"

    return FakeEvent(**field)
