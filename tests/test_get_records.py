from datetime import datetime, timezone

from nonebot import get_driver
from nonebot.adapters import Message
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
    from nonebot_plugin_session import Session, SessionIdType, SessionLevel
    from nonebot_plugin_session.model import get_or_add_session_model

    from nonebot_plugin_chatrecorder.message import serialize_message
    from nonebot_plugin_chatrecorder.model import MessageRecord
    from nonebot_plugin_chatrecorder.record import (
        get_message_records,
        get_message_records_by_session,
        get_messages,
        get_messages_by_session,
        get_messages_plain_text,
        get_messages_plain_text_by_session,
    )

    async with app.test_api() as ctx:
        v11_adapter = V11Adapter(get_driver())
        v11_bot = ctx.create_bot(base=V11Bot, adapter=v11_adapter, self_id="11")
        v12_adapter = V12Adapter(get_driver())
        v12_bot = ctx.create_bot(
            base=V12Bot,
            adapter=v12_adapter,
            self_id="12",
            platform="qq",
            impl="walle-q",
        )
    assert isinstance(v11_bot, V11Bot)
    assert isinstance(v12_bot, V12Bot)

    sessions = [
        Session(
            bot_id="100",
            bot_type="OneBot V11",
            platform="qq",
            level=SessionLevel.LEVEL1,
            id1="1000",
            id2=None,
            id3=None,
        ),
        Session(
            bot_id="101",
            bot_type="OneBot V11",
            platform="qq",
            level=SessionLevel.LEVEL2,
            id1="1000",
            id2="10000",
            id3=None,
        ),
        Session(
            bot_id="100",
            bot_type="OneBot V12",
            platform="qq",
            level=SessionLevel.LEVEL1,
            id1="1001",
            id2=None,
            id3=None,
        ),
        Session(
            bot_id="102",
            bot_type="OneBot V12",
            platform="telegram",
            level=SessionLevel.LEVEL2,
            id1="1002",
            id2="10001",
            id3=None,
        ),
        Session(
            bot_id="103",
            bot_type="OneBot V12",
            platform="kook",
            level=SessionLevel.LEVEL3,
            id1="1003",
            id2="10002",
            id3="100000",
        ),
    ]
    async with create_session() as db_session:
        for session in sessions:
            await get_or_add_session_model(session, db_session)

    records = [
        MessageRecord(
            session_id=1,
            time=datetime.utcfromtimestamp(1000000),
            type="message",
            message_id="1",
            message=serialize_message(v11_bot, V11Msg("test message 1")),
            plain_text="test message 1",
        ),
        MessageRecord(
            session_id=2,
            time=datetime.utcfromtimestamp(1000001),
            type="message_sent",
            message_id="2",
            message=serialize_message(v11_bot, V11Msg("test message 2")),
            plain_text="test message 2",
        ),
        MessageRecord(
            session_id=3,
            time=datetime.utcfromtimestamp(1000002),
            type="message",
            message_id="3",
            message=serialize_message(v12_bot, V12Msg("test message 3")),
            plain_text="test message 3",
        ),
        MessageRecord(
            session_id=4,
            time=datetime.utcfromtimestamp(1000003),
            type="message",
            message_id="3",
            message=serialize_message(v12_bot, V12Msg("test message 4")),
            plain_text="test message 4",
        ),
        MessageRecord(
            session_id=5,
            time=datetime.utcfromtimestamp(1000004),
            type="message",
            message_id="3",
            message=serialize_message(v12_bot, V12Msg("test message 5")),
            plain_text="test message 5",
        ),
    ]
    async with create_session() as db_session:
        for record in records:
            db_session.add(record)
        await db_session.commit()

    msgs = await get_message_records()
    assert len(msgs) == 5
    for msg in msgs:
        assert isinstance(msg, MessageRecord)

    msgs = list(
        filter(
            lambda msg: msg.session.session.get_id(SessionIdType.GROUP)
            == sessions[0].get_id(SessionIdType.GROUP),
            msgs,
        )
    )
    assert len(msgs) == 1

    msgs = await get_messages()
    assert len(msgs) == 5
    for msg in msgs:
        assert isinstance(msg, Message)

    msgs = await get_messages(bot_types=["OneBot V11"])
    assert len(msgs) == 2
    for msg in msgs:
        assert isinstance(msg, V11Msg)

    msgs = await get_messages(bot_types=["OneBot V12"])
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

    msgs = await get_message_records(levels=["LEVEL1"])
    assert len(msgs) == 2
    msgs = await get_message_records(levels=["LEVEL2"])
    assert len(msgs) == 2
    msgs = await get_message_records(levels=["LEVEL3"])
    assert len(msgs) == 1

    msgs = await get_message_records(id1s=["1000"])
    assert len(msgs) == 2
    msgs = await get_message_records(exclude_id1s=["1000"])
    assert len(msgs) == 3

    msgs = await get_message_records(id2s=["10000"])
    assert len(msgs) == 1
    msgs = await get_message_records(exclude_id2s=["10000"])
    assert len(msgs) == 2

    msgs = await get_message_records(id3s=["100000"])
    assert len(msgs) == 1
    msgs = await get_message_records(exclude_id3s=["100000"])
    assert len(msgs) == 0

    # 测试 datetime with timezone
    # postgresql 下如果用含有时区信息的 datetime 作为查询条件，会报错
    # https://github.com/he0119/nonebot-plugin-wordcloud/issues/120
    msgs = await get_message_records(
        time_stop=datetime.utcfromtimestamp(1000002).replace(tzinfo=timezone.utc)
    )
    assert len(msgs) == 3

    msgs = await get_message_records_by_session(sessions[1], SessionIdType.GROUP)
    assert len(msgs) == 1

    msgs = await get_message_records_by_session(sessions[1], SessionIdType.GROUP_USER)
    assert len(msgs) == 1

    msgs = await get_message_records_by_session(sessions[1], SessionIdType.USER)
    assert len(msgs) == 1

    msgs = await get_message_records_by_session(
        sessions[1], SessionIdType.USER, include_bot_id=False
    )
    assert len(msgs) == 2

    msgs = await get_message_records_by_session(sessions[1], SessionIdType.GLOBAL)
    assert len(msgs) == 1

    msgs = await get_message_records_by_session(
        sessions[0], SessionIdType.GLOBAL, include_bot_type=False
    )
    assert len(msgs) == 2

    msgs = await get_messages_by_session(sessions[1], SessionIdType.GROUP)
    assert len(msgs) == 1

    msgs = await get_messages_plain_text_by_session(sessions[1], SessionIdType.GROUP)
    assert len(msgs) == 1
