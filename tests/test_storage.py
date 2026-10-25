import json

import pytest

from models import User, Waypoint
from models.reviews import add_review
from models.routes import add_route
from storage import (load_reviews, load_routes, load_users, read_json_list,
                     save_reviews, save_routes, save_users)
from weather import is_good_weather_for_walk


def test_save_and_load_restores_links(tmp_path):
    users = [User(1, "Анна", "anna@example.com"),
             User(2, "Олег", "oleg@example.com")]
    routes = []
    add_route(routes, "Старый Арбат", "Арбат", 2.1, 10, users[0],
              [Waypoint("Театр Вахтангова", "достопримечательность")])
    reviews = []
    add_review(reviews, routes[0], users[1], 5, "Красиво")

    save_users(users, tmp_path / "users.json")
    save_routes(routes, tmp_path / "routes.json")
    save_reviews(reviews, tmp_path / "reviews.json")

    loaded_users = load_users(tmp_path / "users.json")
    loaded_routes = load_routes(loaded_users, tmp_path / "routes.json")
    loaded_reviews = load_reviews(loaded_routes, loaded_users,
                                  tmp_path / "reviews.json")

    route = loaded_routes[0]
    review = loaded_reviews[0]
    assert route.author is loaded_users[0]
    assert route.waypoints[0].name == "Театр Вахтангова"
    assert review.route is route
    assert review.user is loaded_users[1]


def test_json_stores_ids_not_objects(tmp_path):
    users = [User(1, "Анна", "anna@example.com")]
    routes = []
    add_route(routes, "Старый Арбат", "Арбат", 2.1, 10, users[0])
    save_routes(routes, tmp_path / "routes.json")
    data = json.loads((tmp_path / "routes.json").read_text(encoding="utf-8"))
    assert data[0]["author_id"] == 1
    assert "author" not in data[0]


def test_load_route_with_unknown_author(tmp_path):
    users = [User(1, "Анна", "anna@example.com")]
    routes = []
    add_route(routes, "Старый Арбат", "Арбат", 2.1, 10, users[0])
    save_routes(routes, tmp_path / "routes.json")
    with pytest.raises(ValueError):
        load_routes([], tmp_path / "routes.json")


def test_load_missing_file(tmp_path):
    assert read_json_list(tmp_path / "missing.json") == []


def test_load_broken_file(tmp_path):
    filename = tmp_path / "broken.json"
    filename.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError):
        read_json_list(filename)


def test_weather_rain_is_bad():
    is_good, _ = is_good_weather_for_walk(18, is_raining=True)
    assert not is_good
