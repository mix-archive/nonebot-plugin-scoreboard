import sqlite3
from datetime import datetime
from enum import IntEnum, auto
from typing import Annotated

from anyio import Path
from nonebot import get_driver
from nonebot.dependencies import Dependent

DATABASE_DIR = Path() / "data" / "scoreboard.db"

driver = get_driver()


class TemplateType(IntEnum):
    RANKING = auto()
    ADDITION_SUCCESS = auto()
    ADDITION_FAILURE = auto()
    SUBTRACTION_SUCCESS = auto()
    SUBTRACTION_FAILURE = auto()
    ADMIN = auto()


def _adapt_template_type(val: TemplateType):
    return val.value


def _convert_template_type(val: bytes):
    return TemplateType(int.from_bytes(val, "big"))


sqlite3.register_adapter(TemplateType, _adapt_template_type)
sqlite3.register_converter("template_type", _convert_template_type)


def _adapt_datetime(val: datetime):
    return val.isoformat()


def _convert_datetime(val: bytes):
    return datetime.fromisoformat(val.decode())


sqlite3.register_adapter(datetime, _adapt_datetime)
sqlite3.register_converter("datetime", _convert_datetime)


@driver.on_startup
async def database_on_startup():
    conn = sqlite3.connect(DATABASE_DIR)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS scoreboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            last_update DATETIME NOT NULL,
            score INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS group_score_index ON scoreboard (group_id, score);
        CREATE INDEX IF NOT EXISTS user_group_index ON scoreboard (user_id, group_id) UNIQUE;
        CREATE TABLE IF NOT EXISTS scoring_template (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            template_type TEMPLATE_TYPE NOT NULL,
            template TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS group_template_index ON
            scoring_template (group_id, template_type) UNIQUE;
        """  # noqa: E501
    )
    conn.close()


def _database_cursor():
    return sqlite3.connect(DATABASE_DIR, autocommit=True).cursor()


DatabaseCursor = Annotated[sqlite3.Cursor, Dependent(_database_cursor)]
