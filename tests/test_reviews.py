import pytest

from models import Review, Route, User
from models.reviews import (add_review, delete_review, delete_route_reviews,
                            get_average_rating, get_route_reviews)


def make_objects() -> tuple[Route, User, User]:
    author = User(1, "Анна", "anna@example.com")
    walker = User(2, "Олег", "oleg@example.com")
    route = Route(1, "Старый Арбат", "Арбат", 2.1, 10, author)
    return route, author, walker


def test_review_creation():
    route, _, walker = make_objects()
    review = Review(1, route, walker, 5, "Отлично")
    assert review.route is route
    assert review.user is walker
    assert review.route.name == "Старый Арбат"
    assert review.is_positive()


def test_review_with_invalid_rating():
    route, _, walker = make_objects()
    assert not Review.validate_rating(6)
    with pytest.raises(ValueError):
        Review(1, route, walker, 0)


def test_add_review():
    route, _, walker = make_objects()
    reviews = []
    review = add_review(reviews, route, walker, 4, "Хорошо")
    assert review is not None
    assert reviews == [review]


def test_second_review_from_same_user_forbidden():
    route, author, walker = make_objects()
    reviews = []
    add_review(reviews, route, walker, 5)
    assert add_review(reviews, route, walker, 1) is None
    assert add_review(reviews, route, author, 4) is not None
    assert len(reviews) == 2


def test_get_average_rating():
    route, author, walker = make_objects()
    reviews = []
    assert get_average_rating(reviews, route) is None
    add_review(reviews, route, author, 5)
    add_review(reviews, route, walker, 4)
    assert get_average_rating(reviews, route) == 4.5
    assert len(get_route_reviews(reviews, route)) == 2


def test_delete_reviews():
    route, author, walker = make_objects()
    reviews = []
    add_review(reviews, route, author, 5)
    add_review(reviews, route, walker, 4)
    delete_review(reviews, 1)
    assert [review.id for review in reviews] == [2]
    assert delete_route_reviews(reviews, route) == 1
    assert reviews == []
    with pytest.raises(LookupError):
        delete_review(reviews, 1)
