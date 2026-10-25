from datetime import date

import pytest

from models import Route, User, Waypoint
from models.routes import (add_route, calculate_duration_minutes,
                           delete_route, filter_routes, find_routes,
                           get_difficulty_level, get_route_by_id,
                           sort_routes)


def make_user() -> User:
    return User(1, "Никита", "nikita@example.com")


def make_routes() -> list[Route]:
    author = make_user()
    routes = []
    add_route(routes, "Прогулка по набережной", "Хамовники", 4.5, 60,
              author, [Waypoint("Крымский мост"), Waypoint("Музеон", "парк")])
    add_route(routes, "Старый Арбат", "Арбат", 2.1, 10,
              author, [Waypoint("Театр Вахтангова")])
    add_route(routes, "Лосиный остров", "Сокольники", 11.8, 140,
              author, [Waypoint("Майский просек", "парк")])
    return routes


def test_route_creation():
    author = make_user()
    route = Route(1, "Старый Арбат", "Арбат", 2.1, 10, author,
                  created_at=date(2026, 9, 20))
    assert route.id == 1
    assert route.name == "Старый Арбат"
    assert route.author is author
    assert route.waypoints == []
    assert str(route) == "1. Старый Арбат (Арбат) — 2.1 км, лёгкий"


def test_route_with_invalid_length():
    with pytest.raises(ValueError):
        Route(1, "Маршрут", "Арбат", 0, 10, make_user())
    assert not Route.validate_length(-1)


def test_route_difficulty_and_duration():
    route = Route(1, "Набережная", "Хамовники", 4.5, 60, make_user())
    assert route.difficulty == "средний"
    assert route.duration_minutes() == 68
    assert route.duration_minutes(4.5) == 60


def test_route_add_waypoint():
    route = Route(1, "Набережная", "Хамовники", 4.5, 60, make_user())
    route.add_waypoint(Waypoint("Музеон", "парк"))
    assert [point.name for point in route.waypoints] == ["Музеон"]


def test_get_difficulty_level():
    assert get_difficulty_level(2.1, 10) == "лёгкий"
    assert get_difficulty_level(4.5, 60) == "средний"
    assert get_difficulty_level(11.8, 140) == "сложный"


def test_calculate_duration_minutes():
    assert calculate_duration_minutes(4.5, 4.0) == 68
    with pytest.raises(ValueError):
        calculate_duration_minutes(4.5, 0)


def test_add_route():
    routes = make_routes()
    assert len(routes) == 3
    assert routes[2].id == 3
    assert isinstance(routes[2], Route)


def test_find_routes_by_waypoint():
    found = find_routes(make_routes(), "музеон")
    assert [route.id for route in found] == [1]


def test_filter_routes_by_difficulty_and_length():
    routes = make_routes()
    assert len(filter_routes(routes, difficulty="лёгкий")) == 1
    assert len(filter_routes(routes, max_length_km=5)) == 2
    assert len(filter_routes(routes, district="арбат")) == 1


def test_sort_routes_by_length():
    sorted_routes = sort_routes(make_routes(), "length")
    assert [route.id for route in sorted_routes] == [2, 1, 3]


def test_get_and_delete_route():
    routes = make_routes()
    assert get_route_by_id(routes, 2).name == "Старый Арбат"
    delete_route(routes, 2)
    with pytest.raises(LookupError):
        get_route_by_id(routes, 2)
