"""Тесты базы данных SQLite: схема, импорт из JSON и SQL-запросы."""

import sqlite3
from contextlib import closing

import pytest

from db.database import get_connection
from db.import_json import import_data
from db.queries import QUERIES, fetch_all, fetch_one, load_queries
from models.routes import get_difficulty_level
from storage import load_reviews, load_routes, load_users


def test_schema_has_tables_and_view(db_conn):
    names = {row["name"] for row in db_conn.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
    )}
    assert {"users", "routes", "waypoints", "reviews",
            "route_details"} <= names


def test_import_copies_all_json_records(db_conn):
    users = load_users()
    routes = load_routes(users)
    reviews = load_reviews(routes, users)
    count = db_conn.execute
    assert count("SELECT COUNT(*) FROM users").fetchone()[0] == len(users)
    assert count("SELECT COUNT(*) FROM routes").fetchone()[0] == len(routes)
    assert count("SELECT COUNT(*) FROM reviews").fetchone()[0] == len(reviews)
    assert count("SELECT COUNT(*) FROM waypoints").fetchone()[0] == sum(
        len(route.waypoints) for route in routes
    )


def test_import_can_be_repeated(tmp_path):
    with closing(get_connection(tmp_path / "db.sqlite", create=True)) as conn:
        first = import_data(conn)
        second = import_data(conn)
        assert first == second


def test_foreign_keys_are_checked(db_conn):
    with pytest.raises(sqlite3.IntegrityError):
        db_conn.execute(
            "INSERT INTO reviews (route_id, user_id, rating, created_at) "
            "VALUES (999, 1, 5, '2026-10-01')"
        )


def test_second_review_from_same_user_rejected(db_conn):
    review = db_conn.execute(
        "SELECT route_id, user_id FROM reviews"
    ).fetchone()
    with pytest.raises(sqlite3.IntegrityError):
        db_conn.execute(
            "INSERT INTO reviews (route_id, user_id, rating, created_at) "
            "VALUES (?, ?, 5, '2026-10-01')",
            (review["route_id"], review["user_id"]),
        )


def test_missing_database_is_reported(tmp_path):
    with pytest.raises(FileNotFoundError):
        get_connection(tmp_path / "missing.sqlite")


def test_queries_file_has_named_queries():
    assert len(QUERIES) >= 10
    assert load_queries()["districts"].startswith("-- 5.")


def test_sql_difficulty_matches_python():
    for route in load_routes(load_users()):
        row = fetch_one("public_route_by_id", {"route_id": route.id})
        if route.is_public:
            assert row["difficulty"] == get_difficulty_level(
                route.length_km, route.elevation_gain_m)
            assert row["duration_minutes"] == route.duration_minutes()
        else:
            assert row is None


def test_public_routes_exclude_private():
    routes = load_routes(load_users())
    rows = fetch_all("public_routes")
    assert {row["id"] for row in rows} == {
        route.id for route in routes if route.is_public
    }


def test_search_routes_with_filters():
    rows = fetch_all("search_routes", {
        "difficulty": "средний", "max_length_km": 5, "district": None,
    })
    assert rows
    assert all(row["difficulty"] == "средний" and row["length_km"] <= 5
               for row in rows)
    no_filter = fetch_all("search_routes", {
        "difficulty": None, "max_length_km": None, "district": None,
    })
    assert len(no_filter) == len(fetch_all("public_routes"))


def test_popular_routes_having():
    rows = fetch_all("popular_routes", {"min_reviews": 2})
    assert rows
    assert all(row["reviews_count"] >= 2 for row in rows)


def test_stats_by_district_sums_up():
    rows = fetch_all("stats_by_district")
    totals = fetch_one("totals")
    assert sum(row["routes_count"] for row in rows) == totals["routes_count"]
