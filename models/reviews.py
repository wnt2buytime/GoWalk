"""Класс Review и функции работы с отзывами о маршрутах."""

from datetime import date

from .routes import Route
from .users import User

MIN_RATING = 1
MAX_RATING = 5


class Review:
    """Отзыв пользователя о пройденном маршруте."""

    def __init__(
        self,
        review_id: int,
        route: Route,
        user: User,
        rating: int,
        text: str = "",
        created_at: date | None = None
    ) -> None:
        """Создать объект отзыва.

        Оценка должна быть от MIN_RATING до MAX_RATING.
        """
        if not Review.validate_rating(rating):
            raise ValueError(
                f"Оценка должна быть от {MIN_RATING} до {MAX_RATING}"
            )
        self.id = review_id
        self.route = route
        self.user = user
        self.rating = rating
        self.text = text.strip()
        self.created_at = created_at or date.today()

    @staticmethod
    def validate_rating(rating: int) -> bool:
        """Проверить, что оценка входит в допустимый диапазон."""
        return MIN_RATING <= rating <= MAX_RATING

    def is_positive(self) -> bool:
        """Проверить, является ли отзыв положительным (4 и выше)."""
        return self.rating >= 4

    def __str__(self) -> str:
        """Вернуть строковое представление отзыва."""
        return (f"{self.user.name}, {self.created_at}, "
                f"оценка {self.rating}: {self.text}")


def has_user_review(reviews: list[Review], route: Route, user: User) -> bool:
    """Проверить, оставлял ли пользователь отзыв о маршруте."""
    return any(review.route is route and review.user is user
               for review in reviews)


def add_review(
    reviews: list[Review],
    route: Route,
    user: User,
    rating: int,
    text: str = "",
    created_at: date | None = None
) -> Review | None:
    """Создать отзыв и добавить его в коллекцию.

    Пользователь может оставить только один отзыв о маршруте:
    при повторной попытке отзыв не создаётся и возвращается None.
    """
    if has_user_review(reviews, route, user):
        return None
    review_id = max((review.id for review in reviews), default=0) + 1
    review = Review(review_id, route, user, rating, text, created_at)
    reviews.append(review)
    return review


def find_review_by_id(
    reviews: list[Review],
    review_id: int
) -> Review | None:
    """Найти отзыв по идентификатору или вернуть None."""
    for review in reviews:
        if review.id == review_id:
            return review
    return None


def get_route_reviews(reviews: list[Review], route: Route) -> list[Review]:
    """Вернуть отзывы о маршруте."""
    return [review for review in reviews if review.route is route]


def get_average_rating(reviews: list[Review], route: Route) -> float | None:
    """Вернуть среднюю оценку маршрута или None, если отзывов нет."""
    ratings = [review.rating for review in get_route_reviews(reviews, route)]
    if not ratings:
        return None
    return round(sum(ratings) / len(ratings), 1)


def get_ratings(
    reviews: list[Review],
    routes: list[Route]
) -> dict[int, float | None]:
    """Вернуть словарь «идентификатор маршрута — средняя оценка»."""
    return {route.id: get_average_rating(reviews, route) for route in routes}


def delete_review(reviews: list[Review], review_id: int) -> Review:
    """Удалить отзыв по идентификатору и вернуть его."""
    review = find_review_by_id(reviews, review_id)
    if review is None:
        raise LookupError(f"Отзыв с номером {review_id} не найден")
    reviews.remove(review)
    return review


def delete_route_reviews(reviews: list[Review], route: Route) -> int:
    """Удалить все отзывы о маршруте и вернуть их количество."""
    kept = [review for review in reviews if review.route is not route]
    deleted_count = len(reviews) - len(kept)
    reviews[:] = kept
    return deleted_count


def show_reviews(reviews: list[Review]) -> None:
    """Вывести список отзывов."""
    if not reviews:
        print("Отзывов пока нет.")
    for review in reviews:
        print(f"- {review}")
