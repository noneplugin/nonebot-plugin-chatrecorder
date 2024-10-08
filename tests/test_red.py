from datetime import datetime, timezone

from nonebot import get_driver
from nonebot.adapters.red import Adapter, Bot, Message
from nonebot.adapters.red.api.model import ChatType, Element, MsgType, RoleInfo
from nonebot.adapters.red.config import BotInfo
from nonebot.adapters.red.event import GroupMessageEvent, PrivateMessageEvent
from nonebot.compat import type_validate_python
from nonebug.app import App

from .utils import check_record


async def fake_private_message_event(
    bot: Bot, content: str, msg_id: str
) -> PrivateMessageEvent:
    message = Message(content)
    elements_dict = await message.export(bot)
    elements = [type_validate_python(Element, element) for element in elements_dict]
    return PrivateMessageEvent(
        message=message,
        original_message=message,
        msgId=msg_id,
        msgRandom="196942265",
        msgSeq="103",
        cntSeq="0",
        chatType=ChatType.FRIEND,
        msgType=MsgType.normal,
        subMsgType=1,
        sendType=0,
        senderUid="4321",
        senderUin="1234",
        peerUid="4321",
        peerUin="1234",
        channelId="",
        guildId="",
        guildCode="0",
        fromUid="0",
        fromAppid="0",
        msgTime="1693364414",
        msgMeta="0x",
        sendStatus=2,
        sendMemberName="",
        sendNickName="",
        guildName="",
        channelName="",
        elements=elements,
        records=[],
        emojiLikesList=[],
        commentCnt="0",
        directMsgFlag=0,
        directMsgMembers=[],
        peerName="",
        editable=False,
        avatarMeta="",
        avatarPendant="",
        feedId="",
        roleId="0",
        timeStamp="0",
        isImportMsg=False,
        atType=0,
        roleType=0,
        fromChannelRoleInfo=RoleInfo(roleId="0", name="", color=0),
        fromGuildRoleInfo=RoleInfo(roleId="0", name="", color=0),
        levelRoleInfo=RoleInfo(roleId="0", name="", color=0),
        recallTime="0",
        isOnlineMsg=True,
        generalFlags="0x",
        clientSeq="27516",
        nameType=0,
        avatarFlag=0,
    )


async def fake_group_message_event(
    bot: Bot, content: str, msg_id: str
) -> GroupMessageEvent:
    message = Message(content)
    elements_dict = await message.export(bot)
    elements = [type_validate_python(Element, element) for element in elements_dict]
    return GroupMessageEvent(
        message=message,
        original_message=message,
        msgId=msg_id,
        msgRandom="196942265",
        msgSeq="103",
        cntSeq="0",
        chatType=ChatType.GROUP,
        msgType=MsgType.normal,
        subMsgType=1,
        sendType=0,
        senderUid="4321",
        senderUin="1234",
        peerUid="1111",
        peerUin="1111",
        channelId="",
        guildId="",
        guildCode="0",
        fromUid="0",
        fromAppid="0",
        msgTime="1693364354",
        msgMeta="0x",
        sendStatus=2,
        sendMemberName="",
        sendNickName="",
        guildName="",
        channelName="",
        elements=elements,
        records=[],
        emojiLikesList=[],
        commentCnt="0",
        directMsgFlag=0,
        directMsgMembers=[],
        peerName="",
        editable=False,
        avatarMeta="",
        avatarPendant="",
        feedId="",
        roleId="0",
        timeStamp="0",
        isImportMsg=False,
        atType=0,
        roleType=0,
        fromChannelRoleInfo=RoleInfo(roleId="0", name="", color=0),
        fromGuildRoleInfo=RoleInfo(roleId="0", name="", color=0),
        levelRoleInfo=RoleInfo(roleId="0", name="", color=0),
        recallTime="0",
        isOnlineMsg=True,
        generalFlags="0x",
        clientSeq="27516",
        nameType=0,
        avatarFlag=0,
    )


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_chatrecorder.message import serialize_message

    private_msg = "test private message"
    private_msg_id = "7272944767457625851"

    group_msg = "test group message"
    group_msg_id = "7272944513098472702"

    async with app.test_matcher() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot,
            adapter=adapter,
            self_id="2233",
            info=BotInfo(port=1234, token="1234"),
        )

        event = await fake_private_message_event(bot, private_msg, private_msg_id)
        ctx.receive_event(bot, event)

        event = await fake_group_message_event(bot, group_msg, group_msg_id)
        ctx.receive_event(bot, event)

    await check_record(
        "2233",
        "RedProtocol",
        "qq",
        1,
        "1234",
        None,
        None,
        datetime.fromtimestamp(1693364414, timezone.utc),
        "message",
        private_msg_id,
        serialize_message(bot, Message(private_msg)),
        private_msg,
    )

    await check_record(
        "2233",
        "RedProtocol",
        "qq",
        2,
        "1234",
        "1111",
        None,
        datetime.fromtimestamp(1693364354, timezone.utc),
        "message",
        group_msg_id,
        serialize_message(bot, Message(group_msg)),
        group_msg,
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_chatrecorder.adapters.red import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        adapter = get_driver()._adapters[Adapter.get_name()]
        bot = ctx.create_bot(
            base=Bot,
            adapter=adapter,
            self_id="2233",
            info=BotInfo(port=1234, token="1234"),
        )

    message = Message("test call_api send_message private message")
    elements = await message.export(bot)
    await record_send_msg(
        bot,
        None,
        "send_message",
        {
            "chat_type": 1,
            "target": "4321",
            "message": elements,
        },
        {
            "msgId": "7288209092947528020",
            "msgRandom": "451139554",
            "msgSeq": "31",
            "cntSeq": "0",
            "chatType": 1,
            "msgType": 2,
            "subMsgType": 1,
            "sendType": 1,
            "senderUin": "2233",
            "peerUin": "4321",
            "channelId": "",
            "guildId": "",
            "guildCode": "0",
            "fromUid": "0",
            "fromAppid": "0",
            "msgTime": "1696918415",
            "msgMeta": "0x",
            "sendStatus": 2,
            "sendMemberName": "",
            "sendNickName": "小Q",
            "guildName": "",
            "channelName": "",
            "elements": elements,
            "records": [],
            "emojiLikesList": [],
            "commentCnt": "0",
            "directMsgFlag": 0,
            "directMsgMembers": [],
            "peerName": "",
            "editable": True,
            "avatarMeta": "",
            "roleId": "0",
            "timeStamp": "0",
            "isImportMsg": False,
            "atType": 0,
            "roleType": 0,
            "fromChannelRoleInfo": {"roleId": "0", "name": "", "color": 0},
            "fromGuildRoleInfo": {"roleId": "0", "name": "", "color": 0},
            "levelRoleInfo": {"roleId": "0", "name": "", "color": 0},
            "recallTime": "0",
            "isOnlineMsg": False,
            "generalFlags": "0x",
            "clientSeq": "64458",
        },
    )
    await check_record(
        "2233",
        "RedProtocol",
        "qq",
        1,
        "4321",
        None,
        None,
        datetime.fromtimestamp(1696918415, timezone.utc),
        "message_sent",
        "7288209092947528020",
        serialize_message(bot, message),
        message.extract_plain_text(),
    )

    message = Message("test call_api send_message group message")
    elements = await message.export(bot)
    await record_send_msg(
        bot,
        None,
        "send_message",
        {
            "chat_type": 1,
            "target": "1111",
            "message": await message.export(bot),
        },
        {
            "msgId": "7288207670514953550",
            "msgRandom": "1250543318",
            "msgSeq": "21842",
            "cntSeq": "0",
            "chatType": 2,
            "msgType": 2,
            "subMsgType": 1,
            "sendType": 1,
            "senderUin": "2233",
            "peerUid": "1111",
            "peerUin": "1111",
            "channelId": "",
            "guildId": "",
            "guildCode": "0",
            "fromUid": "0",
            "fromAppid": "0",
            "msgTime": "1696918084",
            "msgMeta": "0x",
            "sendStatus": 2,
            "sendMemberName": "",
            "sendNickName": "小Q",
            "guildName": "",
            "channelName": "",
            "elements": elements,
            "records": [],
            "emojiLikesList": [],
            "commentCnt": "0",
            "directMsgFlag": 0,
            "directMsgMembers": [],
            "peerName": "小Q",
            "editable": True,
            "avatarMeta": "",
            "roleId": "0",
            "timeStamp": "0",
            "isImportMsg": False,
            "atType": 0,
            "roleType": 0,
            "fromChannelRoleInfo": {"roleId": "0", "name": "", "color": 0},
            "fromGuildRoleInfo": {"roleId": "0", "name": "", "color": 0},
            "levelRoleInfo": {"roleId": "0", "name": "", "color": 0},
            "recallTime": "0",
            "isOnlineMsg": False,
            "generalFlags": "0x",
            "clientSeq": "45355",
        },
    )
    await check_record(
        "2233",
        "RedProtocol",
        "qq",
        2,
        None,
        "1111",
        None,
        datetime.fromtimestamp(1696918084, timezone.utc),
        "message_sent",
        "7288207670514953550",
        serialize_message(bot, message),
        message.extract_plain_text(),
    )
