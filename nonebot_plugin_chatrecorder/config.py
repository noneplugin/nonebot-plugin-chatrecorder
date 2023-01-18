from typing import Optional

from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    chatrecorder_record_send_msg: bool = True
    chatrecorder_record_migration_bot_id: Optional[str] = None
