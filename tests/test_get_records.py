from datetime import datetime, timezone

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Adapter as V11Adapter
from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v11 import Message as V11Msg
from nonebot.adapters.onebot.v12 import Adapter as V12Adapter
from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot.adapters.onebot.v12 import Message as V12Msg
from nonebug.app import App


async def test_get_message_records(app: App):
    """测试获取消息记录"""
    from nonebot_plugin_datastore import create_session

    from nonebot_plugin_chatrecorder.message import serialize_message
    from nonebot_plugin_chatrecorder.model import MessageRecord
    from nonebot_plugin_chatrecorder.record import (
        get_message_records,
        get_messages,
        get_messages_plain_text,
    )

    async with app.test_api() as ctx:
        v11_adapter = V11Adapter(get_driver())
        v11_bot = ctx.create_bot(base=V11Bot, adapter=v11_adapter, self_id="11")
        v12_adapter = V12Adapter(get_driver())
        v12_bot = ctx.create_bot(
            base=V12Bot, adapter=v12_adapter, self_id="12", platform="qq"
        )
    assert isinstance(v11_bot, V11Bot)
    assert isinstance(v12_bot, V12Bot)

    records = [
        MessageRecord(
            bot_type="OneBot V11",
            bot_id="100",
            platform="qq",
            time=datetime.utcfromtimestamp(1000000),
            type="message",
            detail_type="private",
            message_id="1",
            message=serialize_message(V11Msg("test message 1")),
            plain_text="test message 1",
            user_id="1000",
        ),
        MessageRecord(
            bot_type="OneBot V11",
            bot_id="101",
            platform="qq",
            time=datetime.utcfromtimestamp(1000001),
            type="message_sent",
            detail_type="group",
            message_id="2",
            message=serialize_message(V11Msg("test message 2")),
            plain_text="test message 2",
            user_id="101",
            group_id="10000",
        ),
        MessageRecord(
            bot_type="OneBot V12",
            bot_id="100",
            platform="qq",
            time=datetime.utcfromtimestamp(1000002),
            type="message",
            detail_type="private",
            message_id="3",
            message=serialize_message(V12Msg("test message 3")),
            plain_text="test message 3",
            user_id="1001",
        ),
        MessageRecord(
            bot_type="OneBot V12",
            bot_id="102",
            platform="telegram",
            time=datetime.utcfromtimestamp(1000003),
            type="message",
            detail_type="group",
            message_id="3",
            message=serialize_message(V12Msg("test message 4")),
            plain_text="test message 4",
            user_id="1002",
            group_id="10001",
        ),
        MessageRecord(
            bot_type="OneBot V12",
            bot_id="103",
            platform="kook",
            time=datetime.utcfromtimestamp(1000004),
            type="message",
            detail_type="channel",
            message_id="3",
            message=serialize_message(V12Msg("test message 5")),
            plain_text="test message 5",
            user_id="1003",
            guild_id="10000",
            channel_id="100000",
        ),
    ]

    async with create_session() as session:
        for record in records:
            session.add(record)
        await session.commit()

    msgs = await get_message_records()
    assert len(msgs) == 5
    for msg in msgs:
        assert isinstance(msg, MessageRecord)

    msgs = await get_messages(v11_bot)
    assert len(msgs) == 2
    for msg in msgs:
        assert isinstance(msg, V11Msg)

    msgs = await get_messages(v12_bot)
    assert len(msgs) == 3
    for msg in msgs:
        assert isinstance(msg, V12Msg)

    msgs = await get_messages_plain_text()
    assert len(msgs) == 5
    for msg in msgs:
        assert isinstance(msg, str)

    msgs = await get_message_records(bot_types=["OneBot V11"])
    assert len(msgs) == 2
    msgs = await get_message_records(bot_types=["OneBot V12"])
    assert len(msgs) == 3

    msgs = await get_message_records(bot_ids=["100"])
    assert len(msgs) == 2
    msgs = await get_message_records(bot_ids=["101", "102", "103"])
    assert len(msgs) == 3

    msgs = await get_message_records(platforms=["qq"])
    assert len(msgs) == 3
    msgs = await get_message_records(platforms=["telegram", "kook"])
    assert len(msgs) == 2

    msgs = await get_message_records(
        time_start=datetime.utcfromtimestamp(1000000),
        time_stop=datetime.utcfromtimestamp(1000004),
    )
    assert len(msgs) == 5
    msgs = await get_message_records(time_start=datetime.utcfromtimestamp(1000002))
    assert len(msgs) == 3
    msgs = await get_message_records(time_stop=datetime.utcfromtimestamp(1000002))
    assert len(msgs) == 3

    msgs = await get_message_records(types=["message"])
    assert len(msgs) == 4
    msgs = await get_message_records(types=["message_sent"])
    assert len(msgs) == 1

    msgs = await get_message_records(detail_types=["private"])
    assert len(msgs) == 2
    msgs = await get_message_records(detail_types=["group"])
    assert len(msgs) == 2
    msgs = await get_message_records(detail_types=["channel"])
    assert len(msgs) == 1

    msgs = await get_message_records(user_ids=["1000"])
    assert len(msgs) == 1
    msgs = await get_message_records(exclude_user_ids=["1000"])
    assert len(msgs) == 4

    msgs = await get_message_records(group_ids=["10000"])
    assert len(msgs) == 1
    msgs = await get_message_records(exclude_group_ids=["10000"])
    assert len(msgs) == 1

    msgs = await get_message_records(guild_ids=["10000"])
    assert len(msgs) == 1
    msgs = await get_message_records(exclude_guild_ids=["10000"])
    assert len(msgs) == 0

    msgs = await get_message_records(channel_ids=["100000"])
    assert len(msgs) == 1
    msgs = await get_message_records(exclude_channel_ids=["100000"])
    assert len(msgs) == 0

    # 测试 datetime with timezone
    # postgresql 下如果用含有时区信息的 datetime 作为查询条件，会报错
    # https://github.com/he0119/nonebot-plugin-wordcloud/issues/120
    msgs = await get_message_records(
        time_stop=datetime.utcfromtimestamp(1000002).replace(tzinfo=timezone.utc)
    )
    assert len(msgs) == 3
