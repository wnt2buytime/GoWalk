"""View-функции раздела отзывов о маршрутах (данные из SQLite)."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.queries import fetch_all, fetch_one


def reviews(request: HttpRequest) -> HttpResponse:
    """Страница со списком отзывов о публичных маршрутах."""
    return render(
        request,
        "reviews/review_list.html",
        {"reviews": fetch_all("review_list")},
    )


def review_detail(request: HttpRequest, review_id: int) -> HttpResponse:
    """Страница отдельного отзыва со связанными маршрутом и автором."""
    review = fetch_one("review_by_id", {"review_id": review_id})
    return render(
        request,
        "reviews/review_detail.html",
        {"review": review},
        status=404 if review is None else 200,
    )
