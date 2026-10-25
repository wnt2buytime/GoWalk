import pytest

from routes import (add_route, calculate_duration_minutes, filter_routes,
                    find_routes, get_difficulty_level, sort_routes)


def make_routes() -> dict[int, dict]:
    routes = {}
    add_route(routes, "Прогулка по набережной", "Хамовники", 4.5, 60,
              ["Крымский мост", "Музеон"], "Никита")
    add_route(routes, "Старый Арбат", "Арбат", 2.1, 10,
              ["Театр Вахтангова"], "Анна")
    add_route(routes, "Лосиный остров", "Сокольники", 11.8, 140,
              ["Майский просек"], "Олег")
    return routes


def test_add_route():
    routes = make_routes()
    assert len(routes) == 3
    assert routes[3]["name"] == "Лосиный остров"


def test_add_route_with_invalid_length():
    with pytest.raises(ValueError):
        add_route({}, "Маршрут", "Арбат", 0, 10, [], "Анна")


def test_get_difficulty_level():
    assert get_difficulty_level(2.1, 10) == "лёгкий"
    assert get_difficulty_level(4.5, 60) == "средний"
    assert get_difficulty_level(11.8, 140) == "сложный"


def test_calculate_duration_minutes():
    assert calculate_duration_minutes(4.5, 4.0) == 68


def test_find_routes_by_waypoint():
    found = find_routes(make_routes(), "музеон")
    assert [route["id"] for route in found] == [1]


def test_filter_routes_by_difficulty_and_length():
    routes = make_routes()
    assert len(filter_routes(routes, difficulty="лёгкий")) == 1
    assert len(filter_routes(routes, max_length_km=5)) == 2


def test_sort_routes_by_length():
    routes = make_routes()
    sorted_routes = sort_routes(list(routes.values()), "length")
    assert [route["id"] for route in sorted_routes] == [2, 1, 3]
