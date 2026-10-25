"""Класс Route и функции работы с пешеходными маршрутами."""

from collections.abc import Iterator
from datetime import date

from .users import User
from .waypoints import Waypoint

DIFFICULTY_LEVELS = ("лёгкий", "средний", "сложный")
DEFAULT_SPEED_KMH = 4.0

SORT_KEYS = {
    "name": lambda route: route.name.lower(),
    "length": lambda route: route.length_km,
    "difficulty": lambda route: DIFFICULTY_LEVELS.index(route.difficulty),
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


class Route:
    """Пешеходный маршрут, составленный пользователем."""

    def __init__(
        self,
        route_id: int,
        name: str,
        district: str,
        length_km: float,
        elevation_gain_m: int,
        author: User,
        waypoints: list[Waypoint] | None = None,
        is_public: bool = True,
        created_at: date | None = None
    ) -> None:
        """Создать объект маршрута.

        При некорректных параметрах выбрасывается ValueError.
        """
        if not name.strip():
            raise ValueError("Название маршрута не может быть пустым")
        if not Route.validate_length(length_km):
            raise ValueError("Длина маршрута должна быть больше нуля")
        if elevation_gain_m < 0:
            raise ValueError("Набор высоты не может быть отрицательным")
        self.id = route_id
        self.name = name.strip()
        self.district = district.strip()
        self.length_km = length_km
        self.elevation_gain_m = elevation_gain_m
        self.author = author
        self.waypoints = list(waypoints or [])
        self.is_public = is_public
        self.created_at = created_at or date.today()

    @staticmethod
    def validate_length(length_km: float) -> bool:
        """Проверить корректность длины маршрута."""
        return length_km > 0

    @property
    def difficulty(self) -> str:
        """Сложность маршрута, вычисляемая по длине и набору высоты."""
        return get_difficulty_level(self.length_km, self.elevation_gain_m)

    def duration_minutes(
        self,
        avg_speed_kmh: float = DEFAULT_SPEED_KMH
    ) -> int:
        """Рассчитать продолжительность прогулки по маршруту."""
        return calculate_duration_minutes(self.length_km, avg_speed_kmh)

    def add_waypoint(self, waypoint: Waypoint) -> None:
        """Добавить точку в конец маршрута."""
        self.waypoints.append(waypoint)

    def matches(self, query: str) -> bool:
        """Проверить, встречается ли подстрока в названии или точках."""
        query = query.strip().lower()
        return (query in self.name.lower()
                or any(point.matches(query) for point in self.waypoints))

    def __str__(self) -> str:
        """Вернуть строковое представление маршрута."""
        return (f"{self.id}. {self.name} ({self.district}) — "
                f"{self.length_km} км, {self.difficulty}")


def add_route(
    routes: list[Route],
    name: str,
    district: str,
    length_km: float,
    elevation_gain_m: int,
    author: User,
    waypoints: list[Waypoint] | None = None,
    is_public: bool = True,
    created_at: date | None = None
) -> Route:
    """Создать маршрут, добавить его в коллекцию и вернуть объект.

    Идентификатор нового маршрута на единицу больше максимального.
    """
    route_id = max((route.id for route in routes), default=0) + 1
    route = Route(route_id, name, district, length_km, elevation_gain_m,
                  author, waypoints, is_public, created_at)
    routes.append(route)
    return route


def find_route_by_id(routes: list[Route], route_id: int) -> Route | None:
    """Найти маршрут по идентификатору или вернуть None."""
    for route in routes:
        if route.id == route_id:
            return route
    return None


def get_route_by_id(routes: list[Route], route_id: int) -> Route:
    """Найти маршрут по идентификатору.

    Если маршрута нет, выбрасывается LookupError.
    """
    route = find_route_by_id(routes, route_id)
    if route is None:
        raise LookupError(f"Маршрут с номером {route_id} не найден")
    return route


def delete_route(routes: list[Route], route_id: int) -> Route:
    """Удалить маршрут из коллекции и вернуть его."""
    route = get_route_by_id(routes, route_id)
    routes.remove(route)
    return route


def find_routes(routes: list[Route], query: str) -> list[Route]:
    """Найти маршруты по подстроке в названии или в точках маршрута."""
    return [route for route in routes if route.matches(query)]


def filter_routes(
    routes: list[Route],
    difficulty: str | None = None,
    max_length_km: float | None = None,
    district: str | None = None
) -> list[Route]:
    """Отобрать маршруты по сложности, максимальной длине и району.

    Параметр со значением None в отборе не участвует.
    """
    return [
        route for route in routes
        if (difficulty is None or route.difficulty == difficulty)
        and (max_length_km is None or route.length_km <= max_length_km)
        and (district is None
             or route.district.lower() == district.lower())
    ]


def iter_public_routes(routes: list[Route]) -> Iterator[Route]:
    """Последовательно выдавать только публичные маршруты."""
    for route in routes:
        if route.is_public:
            yield route


def sort_routes(
    routes: list[Route],
    key: str = "length",
    reverse: bool = False
) -> list[Route]:
    """Вернуть маршруты, упорядоченные по названию, длине или сложности."""
    if key not in SORT_KEYS:
        raise ValueError(f"Неизвестный ключ сортировки: {key}")
    return sorted(routes, key=SORT_KEYS[key], reverse=reverse)


def get_districts(routes: list[Route]) -> list[str]:
    """Вернуть отсортированный список районов без повторов."""
    return sorted({route.district for route in routes})


def show_routes(
    routes: list[Route],
    ratings: dict[int, float | None] | None = None
) -> None:
    """Вывести маршруты в виде таблицы со средней оценкой."""
    if not routes:
        print("Маршруты не найдены.")
        return
    ratings = ratings or {}
    print(f"{'№':>3}  {'Название':<35} {'Район':<15} {'Км':>5}  "
          f"{'Сложность':<9}  Оценка")
    for route in routes:
        rating = ratings.get(route.id)
        rating_text = "нет оценок" if rating is None else f"{rating} из 5"
        print(f"{route.id:>3}  {route.name:<35} {route.district:<15} "
              f"{route.length_km:>5}  {route.difficulty:<9}  {rating_text}")


def show_route_details(route: Route) -> None:
    """Вывести подробную карточку маршрута."""
    print(f"Маршрут: {route.name}")
    print(f"Район: {route.district}")
    print(f"Длина: {route.length_km} км")
    print("Набор высоты: " + str(route.elevation_gain_m) + " м")
    print(f"Сложность: {route.difficulty}")
    print(f"Ожидаемая продолжительность: {route.duration_minutes()} мин")
    print("Точки маршрута:")
    for number, waypoint in enumerate(route.waypoints, start=1):
        print(f"  {number}) {waypoint}")
    print(f"Автор: {route.author.name}")
    print(f"Дата создания: {route.created_at}")
    print(f"Публичный маршрут: {'да' if route.is_public else 'нет'}")
