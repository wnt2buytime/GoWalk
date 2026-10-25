"""View-функции раздела пешеходных маршрутов."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.reviews import get_average_rating, get_route_reviews
from models.routes import (DIFFICULTY_LEVELS, find_route_by_id,
                           iter_public_routes)
from storage import load_reviews, load_routes, load_users


def routes(request: HttpRequest) -> HttpResponse:
    """Страница со списком публичных маршрутов и их оценками."""
    users = load_users()
    routes_list = load_routes(users)
    reviews = load_reviews(routes_list, users)
    context = {
        "routes_with_ratings": [
            (route, get_average_rating(reviews, route))
            for route in iter_public_routes(routes_list)
        ],
        "difficulty_levels": DIFFICULTY_LEVELS,
    }
    return render(request, "routes/route_list.html", context)


def route_detail(request: HttpRequest, route_id: int) -> HttpResponse:
    """Страница отдельного маршрута; скрытый маршрут не показывается."""
    users = load_users()
    routes_list = load_routes(users)
    route = find_route_by_id(routes_list, route_id)
    if route is not None and not route.is_public:
        route = None

    context = {"route": route}
    if route is not None:
        reviews = load_reviews(routes_list, users)
        context["reviews"] = get_route_reviews(reviews, route)
        context["rating"] = get_average_rating(reviews, route)
    return render(
        request,
        "routes/route_detail.html",
        context,
        status=404 if route is None else 200,
    )
