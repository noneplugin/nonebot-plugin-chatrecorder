"""data_migrate

修订 ID: 46327b837dd8
父修订: e6460fccaf90
创建时间: 2023-10-12 15:32:47.496268

"""

from __future__ import annotations

import math
from collections.abc import Sequence

from alembic import op
from alembic.op import run_async
from nonebot import logger, require
from sqlalchemy import Connection, insert, inspect, select
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

revision: str = "46327b837dd8"
down_revision: str | Sequence[str] | None = "e6460fccaf90"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = "71a72119935f"


def _migrate_old_data(ds_conn: Connection):
    insp = inspect(ds_conn)
    if (
        "nonebot_plugin_chatrecorder_messagerecord" not in insp.get_table_names()
        or "nonebot_plugin_chatrecorder_alembic_version" not in insp.get_table_names()
    ):
        return

    DsBase = automap_base()
    DsBase.prepare(autoload_with=ds_conn)
    DsMessageRecord = DsBase.classes.nonebot_plugin_chatrecorder_messagerecord

    Base = automap_base()
    Base.prepare(autoload_with=op.get_bind())
    MessageRecord = Base.classes.nonebot_plugin_chatrecorder_messagerecord

    ds_session = Session(ds_conn)
    session = Session(op.get_bind())

    count = ds_session.query(DsMessageRecord).count()
    if count == 0:
        return

    AlembicVersion = DsBase.classes.nonebot_plugin_chatrecorder_alembic_version
    version_num = ds_session.scalars(select(AlembicVersion.version_num)).one_or_none()
    if not version_num:
        return
    if version_num not in ["902a51ac4032", "44cce443d2c0"]:
        logger.warning(
            "chatrecorder: 发现旧版本的数据，请先安装 0.4.2 版本，"
            "并运行 nb datastore upgrade 完成数据迁移之后再安装新版本"
        )
        raise RuntimeError("chatrecorder: 请先安装 0.4.2 版本完成迁移之后再升级")

    logger.warning(
        "chatrecorder: 发现来自 datastore 的数据，正在迁移，请不要关闭程序..."
    )
    logger.info(f"chatrecorder: 聊天记录数据总数：{count}")

    # 每次迁移的数据量为 10000 条
    migration_limit = 10000
    last_message_id = -1

    for i in range(math.ceil(count / migration_limit)):
        statement = (
            select(
                DsMessageRecord.id,
                DsMessageRecord.session_id,
                DsMessageRecord.time,
                DsMessageRecord.type,
                DsMessageRecord.message_id,
                DsMessageRecord.message,
                DsMessageRecord.plain_text,
            )
            .order_by(DsMessageRecord.id)
            .where(DsMessageRecord.id > last_message_id)
            .limit(migration_limit)
        )
        records = ds_session.execute(statement).all()
        last_message_id = records[-1][0]

        bulk_insert_records = []
        for record in records:
            bulk_insert_records.append(
                {
                    "id": record[0],
                    "session_persist_id": record[1],
                    "time": record[2],
                    "type": record[3],
                    "message_id": record[4],
                    "message": record[5],
                    "plain_text": record[6],
                }
            )
        session.execute(insert(MessageRecord), bulk_insert_records)
        logger.info(
            f"chatrecorder: 已迁移 {i * migration_limit + len(records)}/{count}"
        )

    session.commit()
    logger.warning("chatrecorder: 聊天记录数据迁移完成！")


async def data_migrate(conn: AsyncConnection):
    from nonebot_plugin_datastore.db import get_engine

    async with get_engine().connect() as ds_conn:
        await ds_conn.run_sync(_migrate_old_data)


def upgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###

    try:
        require("nonebot_plugin_datastore")
    except RuntimeError:
        return

    run_async(data_migrate)

    # ### end Alembic commands ###


def downgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
