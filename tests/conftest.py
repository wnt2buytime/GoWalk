"""Общие настройки pytest: тестовая база SQLite и подготовка Django.

Перед импортом модулей проекта путь к базе данных подменяется на
временный файл, который заполняется данными из каталога data/.
Так тесты не зависят от наличия и состояния рабочей базы.
"""

import os
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

TEST_DB_PATH = Path(tempfile.mkdtemp()) / "gowalk_test.sqlite"
os.environ["GOWALK_DB_PATH"] = str(TEST_DB_PATH)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gowalk.settings")

import django  # noqa: E402
import pytest  # noqa: E402
from django.test import Client  # noqa: E402
from django.test.utils import setup_test_environment  # noqa: E402

from db.database import get_connection  # noqa: E402
from db.import_json import import_data  # noqa: E402

with closing(get_connection(TEST_DB_PATH, create=True)) as connection:
    import_data(connection)
    connection.commit()

django.setup()
setup_test_environment()


@pytest.fixture
def client() -> Client:
    """Тестовый клиент Django для запросов к страницам."""
    return Client()


@pytest.fixture
def db_conn() -> sqlite3.Connection:
    """Соединение с тестовой базой данных."""
    with closing(get_connection(TEST_DB_PATH)) as conn:
        yield conn
