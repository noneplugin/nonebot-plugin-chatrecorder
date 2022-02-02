## nonebot-plugin-chatrecorder

适用于 [Nonebot2](https://github.com/nonebot/nonebot2) 的聊天记录插件。


### 安装

- 使用 nb-cli

```
nb plugin install nonebot_plugin_chatrecorder
```

- 使用 pip

```
pip install nonebot_plugin_chatrecorder
```


### 配置

插件会记录机器人收到的消息，可以添加以下配置选择是否记录机器人发出的消息（默认为 `true`）；如果协议端开启了自身消息上报则需设置为 `false` 以避免重复

```
chatrecorder_record_send_msg=true
```


插件依赖 [nonebot-plugin-datastore](https://github.com/he0119/nonebot-plugin-datastore) 插件

消息记录文件存放在 nonebot-plugin-datastore 插件设置的数据目录；同时插件会将消息中 base64 形式的图片、语音等存成文件，放置在 nonebot-plugin-datastore 插件设置的缓存目录，避免消息记录文件体积过大


### 使用

示例：

```python
from datetime import datetime, timedelta
from nonebot_plugin_chatrecorder import get_message_records
from nonebot.adapters.onebot.v11 import GroupMessageEvent

@matcher.handle()
def handle(event: GroupMessageEvent):
    # 获取当前群内成员 '12345' 和 '54321' 1天之内的消息
    msgs = await get_message_records(
        user_ids=['12345', '54321'],
        group_ids=[event.group_id],
        time_start=datetime.utcnow() - timedelta(days=1),
    )
```

详细参数及说明见代码注释


### TODO

 - 咕?
 - 咕咕咕！
