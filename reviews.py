"""Функции для работы с отзывами о маршрутах.

Отзывы хранятся в списке reviews, каждый отзыв — словарь.
"""

from datetime import date

from routes import get_route

MIN_RATING = 1
MAX_RATING = 5


def add_review(
    reviews: list[dict],
    routes: dict[int, dict],
    route_id: int,
    author: str,
    rating: int,
    text: str = "",
    created_at: date | None = None
) -> dict:
    """Добавить отзыв о маршруте и вернуть его данные.

    Маршрут должен существовать, оценка — от MIN_RATING до MAX_RATING.
    """
    get_route(routes, route_id)
    if not MIN_RATING <= rating <= MAX_RATING:
        raise ValueError(
            f"Оценка должна быть от {MIN_RATING} до {MAX_RATING}"
        )

    review_id = max((review["id"] for review in reviews), default=0) + 1
    review = {
        "id": review_id,
        "route_id": route_id,
        "author": author.strip(),
        "rating": rating,
        "text": text.strip(),
        "created_at": (created_at or date.today()).isoformat(),
    }
    reviews.append(review)
    return review


def get_route_reviews(reviews: list[dict], route_id: int) -> list[dict]:
    """Вернуть отзывы о маршруте."""
    return [review for review in reviews if review["route_id"] == route_id]


def get_average_rating(reviews: list[dict], route_id: int) -> float | None:
    """Вернуть среднюю оценку маршрута или None, если отзывов нет."""
    ratings = [review["rating"]
               for review in get_route_reviews(reviews, route_id)]
    if not ratings:
        return None
    return round(sum(ratings) / len(ratings), 1)


def delete_review(reviews: list[dict], review_id: int) -> dict:
    """Удалить отзыв по идентификатору и вернуть его данные."""
    for index, review in enumerate(reviews):
        if review["id"] == review_id:
            return reviews.pop(index)
    raise LookupError(f"Отзыв с номером {review_id} не найден")


def delete_route_reviews(reviews: list[dict], route_id: int) -> int:
    """Удалить все отзывы о маршруте и вернуть их количество."""
    kept = [review for review in reviews if review["route_id"] != route_id]
    deleted_count = len(reviews) - len(kept)
    reviews[:] = kept
    return deleted_count
