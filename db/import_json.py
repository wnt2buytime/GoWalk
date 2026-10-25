"""Перенос данных проекта из JSON-файлов в базу данных SQLite.

Запуск из корня проекта: python -m db.import_json
Скрипт можно запускать повторно: таблицы очищаются и заполняются заново.
"""

import sqlite3
from pathlib import Path

from db.database import DB_PATH, create_schema, get_connection
from storage import (REVIEWS_FILE, ROUTES_FILE, USERS_FILE, load_reviews,
                     load_routes, load_users)


def import_data(
    conn: sqlite3.Connection,
    users_file: Path = USERS_FILE,
    routes_file: Path = ROUTES_FILE,
    reviews_file: Path = REVIEWS_FILE
) -> dict[str, int]:
    """Создать схему и перенести в неё данные из JSON.

    Данные загружаются через storage.py, поэтому проходят те же проверки,
    что и в консольной версии (связи, оценки, длина маршрута).
    Возвращает количество перенесённых записей по таблицам.
    """
    users = load_users(users_file)
    routes = load_routes(users, routes_file)
    reviews = load_reviews(routes, users, reviews_file)

    create_schema(conn)
    conn.executescript(
        "DELETE FROM reviews; DELETE FROM waypoints; "
        "DELETE FROM routes; DELETE FROM users;"
    )

    conn.executemany(
        "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
        [(user.id, user.name, user.email) for user in users],
    )
    conn.executemany(
        """
        INSERT INTO routes (id, name, district, length_km,
                            elevation_gain_m, author_id, is_public,
                            created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (route.id, route.name, route.district, route.length_km,
             route.elevation_gain_m, route.author.id, int(route.is_public),
             route.created_at.isoformat())
            for route in routes
        ],
    )
    waypoint_rows = [
        (route.id, position, waypoint.name, waypoint.kind)
        for route in routes
        for position, waypoint in enumerate(route.waypoints, start=1)
    ]
    conn.executemany(
        "INSERT INTO waypoints (route_id, position, name, kind) "
        "VALUES (?, ?, ?, ?)",
        waypoint_rows,
    )
    conn.executemany(
        """
        INSERT INTO reviews (id, route_id, user_id, rating, text, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (review.id, review.route.id, review.user.id, review.rating,
             review.text or None, review.created_at.isoformat())
            for review in reviews
        ],
    )
    return {
        "users": len(users),
        "routes": len(routes),
        "waypoints": len(waypoint_rows),
        "reviews": len(reviews),
    }


def main() -> None:
    """Создать базу данных и перенести в неё данные из JSON."""
    conn = get_connection(DB_PATH, create=True)
    try:
        counts = import_data(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    print(f"База данных {DB_PATH} заполнена:")
    for table, count in counts.items():
        print(f"  {table}: {count}")


if __name__ == "__main__":
    main()
