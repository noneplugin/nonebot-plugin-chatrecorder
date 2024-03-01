<div align="center">

  <a href="https://nonebot.dev/">
    <img src="https://nonebot.dev/logo.png" width="200" height="200" alt="nonebot">
  </a>

# nonebot-plugin-chatrecorder

_✨ [Nonebot2](https://github.com/nonebot/nonebot2) 聊天记录插件 ✨_

<p align="center">
  <img src="https://img.shields.io/github/license/noneplugin/nonebot-plugin-chatrecorder" alt="license">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/nonebot-2.2.0+-red.svg" alt="NoneBot">
  <a href="https://pypi.org/project/nonebot-plugin-chatrecorder">
    <img src="https://badgen.net/pypi/v/nonebot-plugin-chatrecorder" alt="pypi">
  </a>
</p>

</div>

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

> 以下配置项可在 `.env.*` 文件中设置，具体参考 [NoneBot 配置方式](https://nonebot.dev/docs/appendices/config)

#### `chatrecorder_record_send_msg`

- 类型：`bool`
- 默认：`True`
- 说明：是否记录机器人自己发出的消息

### 使用

其他插件可使用本插件提供的接口获取消息记录

先在插件代码最前面声明依赖：

```python
from nonebot import require
require("nonebot_plugin_chatrecorder")
```

使用示例：

> [!NOTE]
>
> 插件依赖 [nonebot-plugin-session](https://github.com/noneplugin/nonebot-plugin-session) 插件来获取会话相关信息
>
> 会话相关字段如 `id1`、`id2`、`id3` 可以查看 `nonebot-plugin-session` 插件中的说明

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

> [!NOTE]
>
> `time_start` 和 `time_stop` 参数 传入的 `datetime` 对象必须为 [感知型对象](https://docs.python.org/zh-cn/3/library/datetime.html#determining-if-an-object-is-aware-or-naive)（即包含时区信息），或者确保其为 UTC 时间

- 获取当前会话成员 1 天之内的消息记录

```python
from nonebot_plugin_session import extract_session, SessionIdType
from nonebot_plugin_chatrecorder import get_message_records

@matcher.handle()
async def _(bot: Bot, event: Event):
    session = extract_session(bot, event)
    records = await get_message_records(
        session=session,
        time_start=datetime.utcnow() - timedelta(days=1),
    )
```

> [!NOTE]
>
> 可以传入 [nonebot-plugin-session](https://github.com/noneplugin/nonebot-plugin-session) 插件获取的 `Session` 对象来筛选消息记录
>
> 传入 `Session` 时可以通过 `id_type` 来控制要筛选的会话级别

- 获取当前 群聊/私聊 除机器人发出的消息外，其他消息的纯本文形式

```python
from nonebot_plugin_session import extract_session, SessionIdType
from nonebot_plugin_chatrecorder import get_messages_plain_text

@matcher.handle()
async def _(bot: Bot, event: Event):
    session = extract_session(bot, event)
    msgs = await get_messages_plain_text(
        session=session,
        id_type=SessionIdType.GROUP,
        types=["message"],
    )
```

详细参数及说明见代码注释

### 旧版本聊天记录迁移

#### `0.1.x` -> `0.2.x`

从 `0.1.x` 版本升级到 `0.2.x` 版本时，需要添加如下配置项以完成迁移

> #### `chatrecorder_record_migration_bot_id`
>
> - 类型：`Optional[str]`
> - 默认：`None`
> - 说明：在旧版本(0.1.x) 时使用的机器人账号(机器人qq号)，用于数据库迁移；若使用过此插件的旧版本则必须配置，数据库迁移完成后可删除；未使用过旧版本可不配置

#### `0.2.x` -> `0.3.x`

从 `0.2.x` 版本升级到 `0.3.x` ~ `0.4.x` 版本时，会自动运行迁移脚本，或运行 `nb datastore upgrade` 进行迁移

若聊天记录很多，迁移可能会花费较长时间，在迁移过程中不要关闭程序

#### `0.4.x` -> `0.5.x`

从 `0.4.x` 版本升级到 `0.5.x` 版本时，插件数据库依赖由 [nonebot-plugin-datastore](https://github.com/he0119/nonebot-plugin-datastore) 迁移至 [nonebot-plugin-orm](https://github.com/nonebot/plugin-orm)

要迁移聊天记录，需要同时安装 `nonebot-plugin-datastore` 和 `nonebot-plugin-orm`，运行 `nb orm upgrade` 进行迁移

若聊天记录很多，迁移可能会花费较长时间，在迁移过程中不要关闭程序

#### `0.2.x` -> `0.5.x`

若要从 `0.2.x` 版本直接升级到 `0.5.x`，需要先升级到 `0.4.x` 版本，运行 `nb datastore upgrade` 完成迁移后，再继续升级

### 其他说明

> [!NOTE]
>
> 由于在 OneBot V11 适配器中，机器人**发送的消息**中可能存在 base64 形式的图片、语音等，
>
> 为避免消息记录文件体积过大，本插件会将 base64 形式的图片、语音等存成文件，并在消息记录中以文件路径替代。
>
> 这些文件会放置在 [nonebot-plugin-localstore](https://github.com/nonebot/plugin-localstore) 插件设置的缓存目录，**建议定期清理**

### 支持的 adapter

- [x] OneBot v11
- [x] OneBot v12
- [x] Console
- [x] Kaiheila
- [x] Telegram
- [x] Feishu
- [x] RedProtocol
- [x] Discord
- [x] DoDo
- [x] Satori
- [x] QQ

### 鸣谢

- [nonebot-plugin-send-anything-anywhere](https://github.com/felinae98/nonebot-plugin-send-anything-anywhere) 项目的灵感来源以及部分实现的参考
- [uy/sun](https://github.com/he0119) 感谢歪日佬的技术支持
