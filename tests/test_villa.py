import json
from datetime import datetime

from nonebot import get_driver
from nonebot.adapters.villa import Adapter, Bot, Message, SendMessageEvent
from nonebot.adapters.villa.config import BotInfo
from nonebug.app import App

from .utils import check_record


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_chatrecorder.adapters.villa import record_recv_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=Adapter(get_driver()),
            self_id="2233",
            bot_info=BotInfo(
                bot_id="2233",
                bot_secret="xxxx",
                pub_key=(
                    "-----BEGIN PUBLIC KEY-----\n"
                    "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC8KTG22btc3g0SjiH9z352/SkQ\n"
                    "QLXcpaQbzBCgV1A410yMKlgRkM3uyO/kJHGBNAiL6JNe0aH9Gjh18jQgq0toKIUe\n"
                    "1GLPXiC9rrwoFj7VS6istJteSfm2vPIwZw98duUlBnK39OjKDhKSh5TOPpgJh9gn\n"
                    "FVaGNJhR9k4pCvbtzQIDAQAB\n"
                    "-----END PUBLIC KEY-----\n"
                ),
            ),
        )

    event = SendMessageEvent.parse_obj(
        {
            "robot": {
                "template": {
                    "id": "2233",
                    "name": "bot",
                    "desc": "",
                    "icon": "",
                    "commands": [{"name": "/echo", "desc": ""}],
                },
                "villa_id": 7788,
            },
            "type": 2,
            "created_at": 1701226761,
            "id": "8ee4c10d-8354-18d7-84df-7e02f034cfd1",
            "send_at": 1701226761000,
            "content": json.dumps(
                {
                    "content": {"text": "test send message", "entities": []},
                    "user": {
                        "portraitUri": "https://bbs-static.miyoushe.com/avatar/avatar40004.png",
                        "extra": {},
                        "name": "user",
                        "alias": "",
                        "id": "114514",
                        "portrait": "https://bbs-static.miyoushe.com/avatar/avatar40004.png",
                    },
                }
            ),
            "villa_id": 7788,
            "from_user_id": 3344,
            "object_name": 1,
            "room_id": 5566,
            "nickname": "user",
            "msg_uid": "123456",
        }
    )
    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "Villa",
        "villa",
        3,
        "3344",
        "5566",
        "7788",
        datetime.utcfromtimestamp(1701226761000 / 1000),
        "message",
        "123456",
        serialize_message(bot, Message("test send message")),
        "test send message",
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_chatrecorder.adapters.villa import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=Adapter(get_driver()),
            self_id="2233",
            bot_info=BotInfo(
                bot_id="2233",
                bot_secret="xxxx",
                pub_key=(
                    "-----BEGIN PUBLIC KEY-----\n"
                    "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC8KTG22btc3g0SjiH9z352/SkQ\n"
                    "QLXcpaQbzBCgV1A410yMKlgRkM3uyO/kJHGBNAiL6JNe0aH9Gjh18jQgq0toKIUe\n"
                    "1GLPXiC9rrwoFj7VS6istJteSfm2vPIwZw98duUlBnK39OjKDhKSh5TOPpgJh9gn\n"
                    "FVaGNJhR9k4pCvbtzQIDAQAB\n"
                    "-----END PUBLIC KEY-----\n"
                ),
            ),
        )

    await record_send_msg(
        bot,
        None,
        "send_message",
        {
            "villa_id": 7788,
            "room_id": 5566,
            "object_name": "MHY:Text",
            "msg_content": '{"content": {"text": "test", "entities": []}}',
        },
        "123457",
    )
    await check_record(
        "2233",
        "Villa",
        "villa",
        3,
        None,
        "5566",
        "7788",
        None,
        "message_sent",
        "123457",
        serialize_message(bot, Message("test")),
        "test",
    )
