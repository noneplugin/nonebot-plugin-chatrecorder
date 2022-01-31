from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    chatrecorder_record_send_msg: bool = True
