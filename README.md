## nonebot-plugin-chatrecorder

适用于 [Nonebot2](https://github.com/nonebot/nonebot2) 的聊天记录插件。

将聊天消息存至数据库中，方便其他插件使用。

### 安装

- 使用 nb-cli

```shell
nb plugin install nonebot_plugin_chatrecorder
```

- 使用 pip

```shell
pip install nonebot_plugin_chatrecorder
```

### 配置项

> 以下配置项可在 `.env.*` 文件中设置，具体参考 [NoneBot 配置方式](https://v2.nonebot.dev/docs/tutorial/configuration#%E9%85%8D%E7%BD%AE%E6%96%B9%E5%BC%8F)

#### `chatrecorder_record_send_msg`
 - 类型：`bool`
 - 默认：`True`
 - 说明：是否记录机器人自己发出的消息

#### `chatrecorder_record_migration_bot_id`
 - 类型：`Optional[str]`
 - 默认：`None`
 - 说明：在旧版本(0.1.x) 时使用的机器人账号(机器人qq号)，用于数据库迁移；若使用过此插件的旧版本则必须配置，数据库迁移完成后可删除；未使用过旧版本可不配置


### 其他说明

插件依赖 [nonebot-plugin-datastore](https://github.com/he0119/nonebot-plugin-datastore) 插件来提供数据库支持

`nonebot-plugin-datastore` 插件默认使用 SQLite 数据库，
消息记录文件会存放在 `nonebot-plugin-datastore` 插件设置的数据目录

> **Note**
> 
> 由于在 OneBot V11 适配器中，机器人**发送的消息**中可能存在 base64 形式的图片、语音等，
> 
> 为避免消息记录文件体积过大，本插件会将 base64 形式的图片、语音等存成文件，并在消息记录中以文件路径替代。
> 
> 这些文件会放置在 `nonebot-plugin-datastore` 插件设置的缓存目录，**建议定期清理**


插件依赖 [nonebot-plugin-session](https://github.com/noneplugin/nonebot-plugin-session) 插件来获取会话相关信息

其中 `id1` 代表“用户级别”的 id，即 `user_id`；

`id2` 代表“群组级别”的 id，如对于 `OneBot V11` 适配器，`id2` 代表 `group_id`，对于 `OneBot V12` 适配器中的单级群组，`id2` 代表群组 id，对于 `OneBot V12` 适配器中的两级群组，`id2` 代表 `channel_id`；

`id3` 代表“两级群组”的 id，如对于 `OneBot V12` 适配器中的两级群组，`id3` 代表 `guild_id`；


### 使用

其他插件可使用本插件提供的接口获取消息记录

先在插件代码最前面声明依赖：
```python
from nonebot import require
require("nonebot_plugin_chatrecorder")
```

使用示例：

 - 获取当前群内成员 "12345" 和 "54321" 1天之内的消息记录

```python
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot_plugin_chatrecorder import get_message_records

@matcher.handle()
async def _(event: GroupMessageEvent):
    records = await get_message_records(
        id1s=["12345", "54321"],
        id2s=[str(event.group_id)],
        time_start=datetime.utcnow() - timedelta(days=1),
    )
```


 - 获取“当前会话”1天之内的消息记录

```python
from nonebot_plugin_session import extract_session
from nonebot_plugin_chatrecorder import get_message_records

@matcher.handle()
async def _(bot: Bot, event: Event):
    session = extract_session(bot, event)
    records = await get_message_records(
        bot_ids=[session.bot_id],
        bot_types=[session.bot_type],
        platforms=[session.platform],
        levels=[session.level],
        id1s=[session.id1],
        id2s=[session.id2],
        id3s=[session.id3],
        time_start=datetime.utcnow() - timedelta(days=1),
    )
```


 - 使用 ["session id"](https://github.com/noneplugin/nonebot-plugin-session) 筛选消息记录

```python
from nonebot_plugin_session import extract_session, SessionIdType
from nonebot_plugin_chatrecorder import get_message_records

@matcher.handle()
async def _(bot: Bot, event: Event):
    session = extract_session(bot, event)
    records = await get_message_records(
        time_start=datetime.utcnow() - timedelta(days=1),
    )
    records = [
        record
        for record in records
        if record.session.session.get_id(SessionIdType.GROUP)
        == session.get_id(SessionIdType.GROUP)
    ]
```


 - 获取所有 OneBot V11 适配器形式的消息

```python
from nonebot.adapters.onebot.v11 import Bot
from nonebot_plugin_chatrecorder import get_messages

@matcher.handle()
async def _(bot: Bot):
    msgs = await get_messages(bot)
```


 - 获取本群除机器人发出的消息外，其他消息的纯本文形式

```python
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot_plugin_chatrecorder import get_messages_plain_text

@matcher.handle()
async def _(event: GroupMessageEvent):
    msgs = await get_messages_plain_text(
        types=["message"],
        group_ids=[str(event.group_id)],
    )
```

详细参数及说明见代码注释
