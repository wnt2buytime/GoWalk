"""Общие настройки pytest: подготовка Django для тестов веб-страниц."""

import os

import django
import pytest
from django.test import Client
from django.test.utils import setup_test_environment

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gowalk.settings")
django.setup()
setup_test_environment()


@pytest.fixture
def client() -> Client:
    """Тестовый клиент Django для запросов к страницам."""
    return Client()
