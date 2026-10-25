"""View-функции главной страницы, статистики и обработчик ошибки 404."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.queries import fetch_all, fetch_one

POPULAR_MIN_REVIEWS = 2


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница: описание сервиса, навигация и показатели."""
    return render(
        request,
        "homepage/index.html",
        {"totals": fetch_one("totals")},
    )


def statistics(request: HttpRequest) -> HttpResponse:
    """Страница статистики по маршрутам, отзывам и пользователям."""
    context = {
        "totals": fetch_one("totals"),
        "by_district": fetch_all("stats_by_district"),
        "by_difficulty": fetch_all("stats_by_difficulty"),
        "popular_routes": fetch_all(
            "popular_routes", {"min_reviews": POPULAR_MIN_REVIEWS}
        ),
        "popular_min_reviews": POPULAR_MIN_REVIEWS,
        "authors": fetch_all("author_activity"),
        "waypoint_kinds": fetch_all("waypoint_kinds"),
    }
    return render(request, "homepage/statistics.html", context)


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Собственная страница ошибки 404 для всего проекта."""
    return render(request, "404.html", status=404)
