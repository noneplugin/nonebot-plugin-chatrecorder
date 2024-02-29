from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    chatrecorder_record_send_msg: bool = True


plugin_config = get_plugin_config(Config)
