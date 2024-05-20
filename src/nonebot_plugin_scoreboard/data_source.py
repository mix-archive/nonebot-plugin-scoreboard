import sqlite3
from datetime import datetime
from enum import IntEnum, auto
from pathlib import Path
from typing import Annotated

from nonebot import get_driver
from nonebot.params import Depends

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
    if not DATABASE_DIR.is_file():
        DATABASE_DIR.parent.mkdir(parents=True, exist_ok=True)
        DATABASE_DIR.touch()
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
        CREATE UNIQUE INDEX IF NOT EXISTS scoreboard_user_group
            ON scoreboard (user_id, group_id);
        CREATE INDEX IF NOT EXISTS scoreboard_group
            ON scoreboard (group_id, score DESC);
        CREATE TABLE IF NOT EXISTS scoring_template (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            template_type TEMPLATE_TYPE NOT NULL,
            template TEXT NOT NULL
        );
        CREATE UNIQUE INDEX IF NOT EXISTS scoring_template_group_type
            ON scoring_template (group_id, template_type);
        """
    )
    conn.close()


async def _database_cursor():
    return sqlite3.connect(
        DATABASE_DIR, detect_types=sqlite3.PARSE_DECLTYPES, autocommit=True
    ).cursor()


DatabaseCursor = Annotated[sqlite3.Cursor, Depends(_database_cursor)]
