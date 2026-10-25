"""Функции для работы с пешеходными маршрутами.

Маршруты хранятся в словаре routes: ключ — идентификатор маршрута,
значение — словарь с данными маршрута.
"""

from collections.abc import Iterator
from datetime import date

DIFFICULTY_LEVELS = ("лёгкий", "средний", "сложный")
DEFAULT_SPEED_KMH = 4.0

SORT_KEYS = {
    "name": lambda route: route["name"].lower(),
    "length": lambda route: route["length_km"],
    "difficulty": lambda route: DIFFICULTY_LEVELS.index(
        get_difficulty_level(route["length_km"], route["elevation_gain_m"])
    ),
}


def get_difficulty_level(length_km: float, elevation_gain_m: int) -> str:
    """Определить сложность маршрута по длине и набору высоты."""
    if length_km <= 3 and elevation_gain_m <= 30:
        return "лёгкий"
    elif length_km <= 7 and elevation_gain_m <= 100:
        return "средний"
    else:
        return "сложный"


def calculate_duration_minutes(
    length_km: float,
    avg_speed_kmh: float = DEFAULT_SPEED_KMH
) -> int:
    """Рассчитать продолжительность прогулки в минутах."""
    if avg_speed_kmh <= 0:
        raise ValueError("Скорость должна быть больше нуля")
    hours = length_km / avg_speed_kmh
    return round(hours * 60)


def add_route(
    routes: dict[int, dict],
    name: str,
    district: str,
    length_km: float,
    elevation_gain_m: int,
    waypoints: list[str],
    author: str,
    is_public: bool = True,
    created_at: date | None = None
) -> dict:
    """Добавить маршрут в словарь routes и вернуть его данные.

    Идентификатор нового маршрута на единицу больше максимального.
    При некорректных параметрах выбрасывается ValueError.
    """
    if not name.strip():
        raise ValueError("Название маршрута не может быть пустым")
    if length_km <= 0:
        raise ValueError("Длина маршрута должна быть больше нуля")
    if elevation_gain_m < 0:
        raise ValueError("Набор высоты не может быть отрицательным")

    route_id = max(routes, default=0) + 1
    route = {
        "id": route_id,
        "name": name.strip(),
        "district": district.strip(),
        "length_km": length_km,
        "elevation_gain_m": elevation_gain_m,
        "waypoints": list(waypoints),
        "author": author.strip(),
        "is_public": is_public,
        "created_at": (created_at or date.today()).isoformat(),
    }
    routes[route_id] = route
    return route


def get_route(routes: dict[int, dict], route_id: int) -> dict:
    """Вернуть маршрут по идентификатору.

    Если маршрута нет, выбрасывается LookupError.
    """
    if route_id not in routes:
        raise LookupError(f"Маршрут с номером {route_id} не найден")
    return routes[route_id]


def delete_route(routes: dict[int, dict], route_id: int) -> dict:
    """Удалить маршрут из словаря routes и вернуть его данные."""
    get_route(routes, route_id)
    return routes.pop(route_id)


def find_routes(routes: dict[int, dict], query: str) -> list[dict]:
    """Найти маршруты по подстроке в названии или в точках маршрута."""
    query = query.strip().lower()
    found = []
    for route in routes.values():
        texts = [route["name"], *route["waypoints"]]
        if any(query in text.lower() for text in texts):
            found.append(route)
    return found


def filter_routes(
    routes: dict[int, dict],
    difficulty: str | None = None,
    max_length_km: float | None = None,
    district: str | None = None
) -> list[dict]:
    """Отобрать маршруты по сложности, максимальной длине и району.

    Параметр со значением None в отборе не участвует.
    """
    return [
        route for route in routes.values()
        if (difficulty is None or get_difficulty_level(
            route["length_km"], route["elevation_gain_m"]) == difficulty)
        and (max_length_km is None or route["length_km"] <= max_length_km)
        and (district is None
             or route["district"].lower() == district.lower())
    ]


def iter_public_routes(routes: dict[int, dict]) -> Iterator[dict]:
    """Последовательно выдавать только публичные маршруты."""
    for route in routes.values():
        if route["is_public"]:
            yield route


def sort_routes(
    routes: list[dict],
    key: str = "length",
    reverse: bool = False
) -> list[dict]:
    """Вернуть маршруты, упорядоченные по названию, длине или сложности."""
    if key not in SORT_KEYS:
        raise ValueError(f"Неизвестный ключ сортировки: {key}")
    return sorted(routes, key=SORT_KEYS[key], reverse=reverse)


def get_districts(routes: dict[int, dict]) -> list[str]:
    """Вернуть отсортированный список районов без повторов."""
    return sorted({route["district"] for route in routes.values()})
