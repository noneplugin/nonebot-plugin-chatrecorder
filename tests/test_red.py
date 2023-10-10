from datetime import datetime

from nonebot import get_driver
from nonebot.adapters.red import Bot, Message
from nonebot.adapters.red.api.model import ChatType, Element, MsgType, RoleInfo
from nonebot.adapters.red.config import BotInfo
from nonebot.adapters.red.event import GroupMessageEvent, PrivateMessageEvent
from nonebug.app import App

from .utils import check_record


async def test_record_recv_msg(app: App):
    """测试记录收到的消息"""
    from nonebot_plugin_chatrecorder.adapters.red import record_recv_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=get_driver()._adapters["RedProtocol"],
            self_id="2233",
            info=BotInfo(port=1234, token="1234"),
        )
    assert isinstance(bot, Bot)

    message = Message("test private message")
    elements_dict = await message.export(bot)
    elements = [Element.parse_obj(element) for element in elements_dict]
    event = PrivateMessageEvent(
        message=message,
        original_message=message,
        msgId="7272944767457625851",
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
    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "RedProtocol",
        "qq",
        1,
        "1234",
        None,
        None,
        datetime.utcfromtimestamp(1693364414),
        "message",
        "7272944767457625851",
        serialize_message(bot, message),
        message.extract_plain_text(),
    )

    message = Message("test group message")
    elements_dict = await message.export(bot)
    elements = [Element.parse_obj(element) for element in elements_dict]
    event = GroupMessageEvent(
        message=message,
        original_message=message,
        msgId="7272944513098472702",
        msgRandom="1526531828",
        msgSeq="831",
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
        sendNickName="uy/sun",
        guildName="",
        channelName="",
        elements=elements,
        records=[],
        emojiLikesList=[],
        commentCnt="0",
        directMsgFlag=0,
        directMsgMembers=[],
        peerName="uy/sun",
        editable=False,
        avatarMeta="",
        avatarPendant="",
        feedId="",
        roleId="0",
        timeStamp="0",
        isImportMsg=False,
        atType=0,
        roleType=None,
        fromChannelRoleInfo=RoleInfo(roleId="0", name="", color=0),
        fromGuildRoleInfo=RoleInfo(roleId="0", name="", color=0),
        levelRoleInfo=RoleInfo(roleId="0", name="", color=0),
        recallTime="0",
        isOnlineMsg=True,
        generalFlags="0x",
        clientSeq="0",
        nameType=0,
        avatarFlag=0,
    )
    await record_recv_msg(bot, event)
    await check_record(
        "2233",
        "RedProtocol",
        "qq",
        2,
        "1234",
        "1111",
        None,
        datetime.utcfromtimestamp(1693364354),
        "message",
        "7272944513098472702",
        serialize_message(bot, message),
        message.extract_plain_text(),
    )


async def test_record_send_msg(app: App):
    """测试记录发送的消息"""
    from nonebot_plugin_chatrecorder.adapters.red import record_send_msg
    from nonebot_plugin_chatrecorder.message import serialize_message

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=Bot,
            adapter=get_driver()._adapters["RedProtocol"],
            self_id="2233",
            info=BotInfo(port=1234, token="1234"),
        )
    assert isinstance(bot, Bot)

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
        datetime.utcfromtimestamp(1696918415),
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
        datetime.utcfromtimestamp(1696918084),
        "message_sent",
        "7288207670514953550",
        serialize_message(bot, message),
        message.extract_plain_text(),
    )
