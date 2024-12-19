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
    from nonebot_plugin_orm import get_session
    from nonebot_plugin_uninfo import (
        Scene,
        SceneType,
        Session,
        SupportAdapter,
        SupportScope,
        User,
    )
    from nonebot_plugin_uninfo.orm import get_session_persist_id

    from nonebot_plugin_chatrecorder.message import serialize_message
    from nonebot_plugin_chatrecorder.model import MessageRecord
    from nonebot_plugin_chatrecorder.record import (
        get_message_records,
        get_messages,
        get_messages_plain_text,
    )

    async with app.test_api() as ctx:
        v11_adapter = get_driver()._adapters[V11Adapter.get_name()]
        v11_bot = ctx.create_bot(base=V11Bot, adapter=v11_adapter, self_id="11")
        v12_adapter = get_driver()._adapters[V12Adapter.get_name()]
        v12_bot = ctx.create_bot(
            base=V12Bot,
            adapter=v12_adapter,
            self_id="12",
            platform="qq",
            impl="walle-q",
        )

    sessions = [
        Session(
            self_id="100",
            adapter=SupportAdapter.onebot11,
            scope=SupportScope.qq_client,
            scene=Scene(id="1000", type=SceneType.PRIVATE),
            user=User(id="1000"),
        ),
        Session(
            self_id="101",
            adapter=SupportAdapter.onebot11,
            scope=SupportScope.qq_client,
            scene=Scene(id="10000", type=SceneType.GROUP),
            user=User(id="1000"),
        ),
        Session(
            self_id="100",
            adapter=SupportAdapter.onebot12,
            scope=SupportScope.qq_client,
            scene=Scene(id="1001", type=SceneType.PRIVATE),
            user=User(id="1001"),
        ),
        Session(
            self_id="102",
            adapter=SupportAdapter.onebot12,
            scope=SupportScope.telegram,
            scene=Scene(id="10001", type=SceneType.GROUP),
            user=User(id="1002"),
        ),
        Session(
            self_id="103",
            adapter=SupportAdapter.onebot12,
            scope=SupportScope.kook,
            scene=Scene(
                id="10002",
                type=SceneType.CHANNEL_TEXT,
                parent=Scene(id="100000", type=SceneType.GUILD),
            ),
            user=User(id="1003"),
        ),
    ]
    session_persist_ids: list[int] = []
    for session in sessions:
        session_persist_id = await get_session_persist_id(session)
        session_persist_ids.append(session_persist_id)

    records = [
        MessageRecord(
            session_persist_id=session_persist_ids[0],
            time=datetime.fromtimestamp(1000000, timezone.utc).replace(tzinfo=None),
            type="message",
            message_id="1",
            message=serialize_message(v11_bot, V11Msg("test message 1")),
            plain_text="test message 1",
        ),
        MessageRecord(
            session_persist_id=session_persist_ids[1],
            time=datetime.fromtimestamp(1000001, timezone.utc).replace(tzinfo=None),
            type="message_sent",
            message_id="2",
            message=serialize_message(v11_bot, V11Msg("test message 2")),
            plain_text="test message 2",
        ),
        MessageRecord(
            session_persist_id=session_persist_ids[2],
            time=datetime.fromtimestamp(1000002, timezone.utc).replace(tzinfo=None),
            type="message",
            message_id="3",
            message=serialize_message(v12_bot, V12Msg("test message 3")),
            plain_text="test message 3",
        ),
        MessageRecord(
            session_persist_id=session_persist_ids[3],
            time=datetime.fromtimestamp(1000003, timezone.utc).replace(tzinfo=None),
            type="message",
            message_id="3",
            message=serialize_message(v12_bot, V12Msg("test message 4")),
            plain_text="test message 4",
        ),
        MessageRecord(
            session_persist_id=session_persist_ids[4],
            time=datetime.fromtimestamp(1000004, timezone.utc).replace(tzinfo=None),
            type="message",
            message_id="3",
            message=serialize_message(v12_bot, V12Msg("test message 5")),
            plain_text="test message 5",
        ),
    ]
    async with get_session() as db_session:
        for record in records:
            db_session.add(record)
        await db_session.commit()

    msgs = await get_message_records()
    assert len(msgs) == 5
    for msg in msgs:
        assert isinstance(msg, MessageRecord)

    msgs = await get_messages()
    assert len(msgs) == 5
    for msg in msgs:
        assert isinstance(msg, Message)

    msgs = await get_messages(adapters=[SupportAdapter.onebot11])
    assert len(msgs) == 2
    for msg in msgs:
        assert isinstance(msg, V11Msg)

    msgs = await get_messages(adapters=[SupportAdapter.onebot12])
    assert len(msgs) == 3
    for msg in msgs:
        assert isinstance(msg, V12Msg)

    msgs = await get_messages_plain_text()
    assert len(msgs) == 5
    for msg in msgs:
        assert isinstance(msg, str)

    msgs = await get_message_records(adapters=[SupportAdapter.onebot11])
    assert len(msgs) == 2
    msgs = await get_message_records(adapters=[SupportAdapter.onebot12])
    assert len(msgs) == 3

    msgs = await get_message_records(self_ids=["100"])
    assert len(msgs) == 2
    msgs = await get_message_records(self_ids=["101", "102", "103"])
    assert len(msgs) == 3

    msgs = await get_message_records(scopes=[SupportScope.qq_client])
    assert len(msgs) == 3
    msgs = await get_message_records(scopes=[SupportScope.telegram, SupportScope.kook])
    assert len(msgs) == 2

    msgs = await get_message_records(
        time_start=datetime.fromtimestamp(1000000, timezone.utc),
        time_stop=datetime.fromtimestamp(1000004, timezone.utc),
    )
    assert len(msgs) == 5
    msgs = await get_message_records(
        time_start=datetime.fromtimestamp(1000002, timezone.utc)
    )
    assert len(msgs) == 3
    msgs = await get_message_records(
        time_stop=datetime.fromtimestamp(1000002, timezone.utc)
    )
    assert len(msgs) == 3
    msgs = await get_message_records(
        time_stop=datetime.fromtimestamp(1000002, timezone.utc).replace(tzinfo=None)
    )
    assert len(msgs) == 3

    msgs = await get_message_records(types=["message"])
    assert len(msgs) == 4
    msgs = await get_message_records(types=["message_sent"])
    assert len(msgs) == 1

    msgs = await get_message_records(scene_types=[SceneType.PRIVATE])
    assert len(msgs) == 2
    msgs = await get_message_records(scene_types=[SceneType.GROUP])
    assert len(msgs) == 2
    msgs = await get_message_records(scene_types=[SceneType.CHANNEL_TEXT])
    assert len(msgs) == 1

    msgs = await get_message_records(user_ids=["1000"])
    assert len(msgs) == 2
    msgs = await get_message_records(exclude_user_ids=["1000"])
    assert len(msgs) == 3

    msgs = await get_message_records(scene_ids=["10000"])
    assert len(msgs) == 1
    msgs = await get_message_records(exclude_scene_ids=["10000"])
    assert len(msgs) == 4

    # msgs = await get_message_records(scene_ids=["100000"])
    # assert len(msgs) == 1
    # msgs = await get_message_records(exclude_scene_ids=["100000"])
    # assert len(msgs) == 4

    msgs = await get_message_records(
        session=sessions[1], filter_scene=True, filter_user=False
    )
    assert len(msgs) == 1

    msgs = await get_message_records(
        session=sessions[0], filter_adapter=False, user_ids=["1001"]
    )
    assert len(msgs) == 0

    msgs = await get_message_records(
        session=sessions[0], filter_adapter=False, user_ids=["1000", "1001"]
    )
    assert len(msgs) == 1

    msgs = await get_message_records(
        session=sessions[1], filter_scene=True, filter_user=True
    )
    assert len(msgs) == 1

    msgs = await get_message_records(
        session=sessions[1], filter_scene=False, filter_user=True
    )
    assert len(msgs) == 1

    msgs = await get_message_records(
        session=sessions[1], filter_scene=False, filter_user=True, filter_self_id=False
    )
    assert len(msgs) == 2

    msgs = await get_message_records(
        session=sessions[1], filter_scene=False, filter_user=False
    )
    assert len(msgs) == 1

    msgs = await get_message_records(
        session=sessions[0], filter_scene=False, filter_user=False, filter_adapter=False
    )
    assert len(msgs) == 2

    msgs = await get_message_records(
        session=sessions[0],
        filter_scene=False,
        filter_user=False,
        filter_adapter=False,
        exclude_user_ids=["1000"],
    )
    assert len(msgs) == 1

    msgs = await get_messages(session=sessions[1], filter_scene=True, filter_user=False)
    assert len(msgs) == 1

    msgs = await get_messages_plain_text(
        session=sessions[1], filter_scene=True, filter_user=False
    )
    assert len(msgs) == 1
