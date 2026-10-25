import pytest

from reviews import add_review, delete_review, get_average_rating
from routes import add_route


def make_routes() -> dict[int, dict]:
    routes = {}
    add_route(routes, "Старый Арбат", "Арбат", 2.1, 10, [], "Анна")
    return routes


def test_add_review():
    reviews = []
    add_review(reviews, make_routes(), 1, "Олег", 5, "Отлично")
    assert len(reviews) == 1
    assert reviews[0]["route_id"] == 1


def test_add_review_for_missing_route():
    with pytest.raises(LookupError):
        add_review([], make_routes(), 42, "Олег", 5)


def test_add_review_with_invalid_rating():
    with pytest.raises(ValueError):
        add_review([], make_routes(), 1, "Олег", 6)


def test_get_average_rating():
    routes = make_routes()
    reviews = []
    add_review(reviews, routes, 1, "Олег", 5)
    add_review(reviews, routes, 1, "Анна", 4)
    assert get_average_rating(reviews, 1) == 4.5
    assert get_average_rating([], 1) is None


def test_delete_review():
    reviews = []
    add_review(reviews, make_routes(), 1, "Олег", 5)
    delete_review(reviews, 1)
    assert reviews == []
