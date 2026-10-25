"""View-функции раздела отзывов о маршрутах."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.reviews import find_review_by_id
from storage import load_reviews, load_routes, load_users


def reviews(request: HttpRequest) -> HttpResponse:
    """Страница со списком отзывов о публичных маршрутах."""
    users = load_users()
    routes_list = load_routes(users)
    context = {
        "reviews": [
            review for review in load_reviews(routes_list, users)
            if review.route.is_public
        ],
    }
    return render(request, "reviews/review_list.html", context)


def review_detail(request: HttpRequest, review_id: int) -> HttpResponse:
    """Страница отдельного отзыва со связанными маршрутом и автором."""
    users = load_users()
    routes_list = load_routes(users)
    review = find_review_by_id(load_reviews(routes_list, users), review_id)
    if review is not None and not review.route.is_public:
        review = None
    return render(
        request,
        "reviews/review_detail.html",
        {"review": review},
        status=404 if review is None else 200,
    )
