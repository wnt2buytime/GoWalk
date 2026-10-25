import pytest

from routes import add_route
from storage import load_routes, read_json_list, save_routes
from utils import parse_waypoints
from weather import is_good_weather_for_walk


def test_save_and_load_routes(tmp_path):
    filename = tmp_path / "routes.json"
    routes = {}
    add_route(routes, "Старый Арбат", "Арбат", 2.1, 10, ["Арбат"], "Анна")
    save_routes(routes, filename)
    assert load_routes(filename) == routes


def test_load_missing_file(tmp_path):
    assert read_json_list(tmp_path / "missing.json") == []


def test_load_broken_file(tmp_path):
    filename = tmp_path / "broken.json"
    filename.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError):
        read_json_list(filename)


def test_parse_waypoints():
    assert parse_waypoints("Музеон, , Крымский мост ") == [
        "Музеон", "Крымский мост"
    ]


def test_weather_rain_is_bad():
    is_good, _ = is_good_weather_for_walk(18, is_raining=True)
    assert not is_good
