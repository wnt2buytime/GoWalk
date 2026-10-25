"""Загрузка и сохранение данных приложения в JSON-файлах."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
ROUTES_FILE = DATA_DIR / "routes.json"
REVIEWS_FILE = DATA_DIR / "reviews.json"


def read_json_list(filename: Path) -> list[dict]:
    """Прочитать список словарей из JSON-файла.

    Если файла нет, возвращается пустой список.
    Если файл повреждён, выбрасывается ValueError.
    """
    try:
        with open(filename, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Файл {filename} содержит некорректный JSON: {error}"
        ) from error

    if not isinstance(data, list):
        raise ValueError(f"Файл {filename} должен содержать список")
    return data


def write_json_list(filename: Path, data: list[dict]) -> None:
    """Записать список словарей в JSON-файл."""
    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_routes(filename: Path = ROUTES_FILE) -> dict[int, dict]:
    """Загрузить маршруты и вернуть словарь «идентификатор — маршрут»."""
    return {route["id"]: route for route in read_json_list(filename)}


def save_routes(routes: dict[int, dict], filename: Path = ROUTES_FILE) -> None:
    """Сохранить маршруты в JSON-файл."""
    write_json_list(filename, list(routes.values()))


def load_reviews(filename: Path = REVIEWS_FILE) -> list[dict]:
    """Загрузить отзывы из JSON-файла."""
    return read_json_list(filename)


def save_reviews(reviews: list[dict], filename: Path = REVIEWS_FILE) -> None:
    """Сохранить отзывы в JSON-файл."""
    write_json_list(filename, reviews)
