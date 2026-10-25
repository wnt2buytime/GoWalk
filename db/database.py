"""Подключение к базе данных SQLite проекта."""

import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_FILE = BASE_DIR / "sql" / "schema.sql"

# Путь можно переопределить переменной окружения (используется в тестах).
DB_PATH = Path(
    os.environ.get("GOWALK_DB_PATH", BASE_DIR / "data" / "gowalk.sqlite")
)


def get_connection(
    db_path: Path = DB_PATH,
    create: bool = False
) -> sqlite3.Connection:
    """Открыть соединение с базой данных.

    Включает проверку внешних ключей и доступ к полям строк по именам.
    Если файла базы нет и create=False, выбрасывается FileNotFoundError:
    иначе SQLite молча создал бы пустую базу без таблиц.
    """
    if not create and not Path(db_path).exists():
        raise FileNotFoundError(
            f"База данных {db_path} не найдена. "
            "Создайте её командой: python -m db.import_json"
        )
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """Создать таблицы и представления из файла sql/schema.sql."""
    conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
