"""Выполнение именованных SQL-запросов из файла sql/queries.sql."""

import sqlite3
from contextlib import closing
from pathlib import Path

from db.database import BASE_DIR, DB_PATH, get_connection

QUERIES_FILE = BASE_DIR / "sql" / "queries.sql"
NAME_PREFIX = "-- name:"


def load_queries(filename: Path = QUERIES_FILE) -> dict[str, str]:
    """Прочитать файл запросов и вернуть словарь «имя — текст запроса».

    Запрос начинается со строки "-- name: <имя>" и продолжается
    до следующей такой строки.
    """
    queries = {}
    name = None
    lines = []
    for line in filename.read_text(encoding="utf-8").splitlines():
        if line.startswith(NAME_PREFIX):
            if name is not None:
                queries[name] = "\n".join(lines).strip()
            name = line.removeprefix(NAME_PREFIX).strip()
            lines = []
        elif name is not None:
            lines.append(line)
    if name is not None:
        queries[name] = "\n".join(lines).strip()
    return queries


QUERIES = load_queries()


def fetch_all(
    name: str,
    params: dict | None = None,
    db_path: Path = DB_PATH
) -> list[sqlite3.Row]:
    """Выполнить запрос по имени и вернуть все строки результата."""
    with closing(get_connection(db_path)) as conn:
        return conn.execute(QUERIES[name], params or {}).fetchall()


def fetch_one(
    name: str,
    params: dict | None = None,
    db_path: Path = DB_PATH
) -> sqlite3.Row | None:
    """Выполнить запрос по имени и вернуть первую строку или None."""
    with closing(get_connection(db_path)) as conn:
        return conn.execute(QUERIES[name], params or {}).fetchone()
