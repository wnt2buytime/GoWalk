"""View-функции главной страницы и обработчик ошибки 404."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.routes import iter_public_routes
from storage import load_reviews, load_routes, load_users


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница: описание сервиса, навигация и статистика."""
    users = load_users()
    routes = load_routes(users)
    reviews = load_reviews(routes, users)
    context = {
        "routes_count": len(list(iter_public_routes(routes))),
        "reviews_count": len(reviews),
        "users_count": len(users),
    }
    return render(request, "homepage/index.html", context)


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Собственная страница ошибки 404 для всего проекта."""
    return render(request, "404.html", status=404)
