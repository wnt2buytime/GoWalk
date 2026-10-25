"""Загрузка и сохранение данных приложения в JSON-файлах.

При загрузке данные JSON преобразуются в объекты User, Route и Review,
при сохранении — обратно в словари. Связи между объектами хранятся
в JSON через идентификаторы (author_id, route_id, user_id).
"""

import json
from datetime import date
from pathlib import Path

from models import Review, Route, User, Waypoint
from models.routes import get_route_by_id
from models.users import get_user_by_id

DATA_DIR = Path(__file__).parent / "data"
USERS_FILE = DATA_DIR / "users.json"
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


def load_users(filename: Path = USERS_FILE) -> list[User]:
    """Загрузить пользователей и вернуть коллекцию объектов User."""
    try:
        return [User.from_data(item) for item in read_json_list(filename)]
    except KeyError as error:
        raise ValueError(f"В файле {filename} нет поля {error}") from error


def save_users(users: list[User], filename: Path = USERS_FILE) -> None:
    """Сохранить пользователей в JSON-файл."""
    write_json_list(filename, [user.to_data() for user in users])


def route_from_data(data: dict, users: list[User]) -> Route:
    """Создать объект Route из словаря JSON, найдя автора по author_id."""
    return Route(
        route_id=data["id"],
        name=data["name"],
        district=data["district"],
        length_km=data["length_km"],
        elevation_gain_m=data["elevation_gain_m"],
        author=get_user_by_id(users, data["author_id"]),
        waypoints=[Waypoint.from_data(item) for item in data["waypoints"]],
        is_public=data["is_public"],
        created_at=date.fromisoformat(data["created_at"]),
    )


def route_to_data(route: Route) -> dict:
    """Преобразовать объект Route в словарь для JSON."""
    return {
        "id": route.id,
        "name": route.name,
        "district": route.district,
        "length_km": route.length_km,
        "elevation_gain_m": route.elevation_gain_m,
        "author_id": route.author.id,
        "waypoints": [waypoint.to_data() for waypoint in route.waypoints],
        "is_public": route.is_public,
        "created_at": route.created_at.isoformat(),
    }


def load_routes(
    users: list[User],
    filename: Path = ROUTES_FILE
) -> list[Route]:
    """Загрузить маршруты и связать их с объектами пользователей."""
    try:
        return [route_from_data(item, users)
                for item in read_json_list(filename)]
    except KeyError as error:
        raise ValueError(f"В файле {filename} нет поля {error}") from error
    except LookupError as error:
        raise ValueError(f"Файл {filename}: {error}") from error


def save_routes(routes: list[Route], filename: Path = ROUTES_FILE) -> None:
    """Сохранить маршруты в JSON-файл."""
    write_json_list(filename, [route_to_data(route) for route in routes])


def review_from_data(
    data: dict,
    routes: list[Route],
    users: list[User]
) -> Review:
    """Создать объект Review, найдя маршрут и пользователя по id."""
    return Review(
        review_id=data["id"],
        route=get_route_by_id(routes, data["route_id"]),
        user=get_user_by_id(users, data["user_id"]),
        rating=data["rating"],
        text=data["text"],
        created_at=date.fromisoformat(data["created_at"]),
    )


def review_to_data(review: Review) -> dict:
    """Преобразовать объект Review в словарь для JSON."""
    return {
        "id": review.id,
        "route_id": review.route.id,
        "user_id": review.user.id,
        "rating": review.rating,
        "text": review.text,
        "created_at": review.created_at.isoformat(),
    }


def load_reviews(
    routes: list[Route],
    users: list[User],
    filename: Path = REVIEWS_FILE
) -> list[Review]:
    """Загрузить отзывы и связать их с маршрутами и пользователями."""
    try:
        return [review_from_data(item, routes, users)
                for item in read_json_list(filename)]
    except KeyError as error:
        raise ValueError(f"В файле {filename} нет поля {error}") from error
    except LookupError as error:
        raise ValueError(f"Файл {filename}: {error}") from error


def save_reviews(
    reviews: list[Review],
    filename: Path = REVIEWS_FILE
) -> None:
    """Сохранить отзывы в JSON-файл."""
    write_json_list(filename, [review_to_data(review) for review in reviews])
