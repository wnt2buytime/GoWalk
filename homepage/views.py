"""View-функции главной страницы и общий каркас страниц проекта."""

from django.http import HttpRequest, HttpResponse

from models.routes import iter_public_routes
from storage import load_reviews, load_routes, load_users

BOOTSTRAP_CSS = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
    "/dist/css/bootstrap.min.css"
)


def page(title: str, content: str) -> str:
    """Собрать HTML-документ с общим каркасом, Bootstrap и навигацией."""
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="{BOOTSTRAP_CSS}">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand bg-success mb-4" data-bs-theme="dark">
        <div class="container">
            <a class="navbar-brand" href="/">GoWalk</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">Главная</a>
                <a class="nav-link" href="/routes/">Маршруты</a>
                <a class="nav-link" href="/reviews/">Отзывы</a>
            </div>
        </div>
    </nav>
    <main class="container pb-5">{content}</main>
</body>
</html>"""


def not_found(title: str, back_url: str, back_text: str) -> HttpResponse:
    """Вернуть страницу «объект не найден» с кодом 404."""
    content = f"""
    <h1 class="text-danger">{title}</h1>
    <a href="{back_url}" class="btn btn-outline-secondary">← {back_text}</a>
    """
    return HttpResponse(page(title, content), status=404)


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница: описание сервиса и навигация."""
    users = load_users()
    routes = load_routes(users)
    reviews = load_reviews(routes, users)
    public_count = len(list(iter_public_routes(routes)))
    content = f"""
    <div class="p-5 mb-4 bg-white rounded-3 shadow-sm">
        <h1 class="display-4">GoWalk</h1>
        <p class="lead">
            Сервис для создания и подбора пешеходных прогулочных маршрутов
            по городу.
        </p>
        <p>
            Маршрутов: {public_count} · отзывов: {len(reviews)} ·
            пользователей: {len(users)}
        </p>
        <a href="/routes/" class="btn btn-success me-2">Маршруты</a>
        <a href="/reviews/" class="btn btn-outline-success">Отзывы</a>
    </div>
    """
    return HttpResponse(page("GoWalk", content))


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Собственная страница ошибки 404 для всего проекта."""
    content = """
    <h1 class="text-danger">404 — страница не найдена</h1>
    <p>Проверьте адрес или вернитесь на главную.</p>
    <a href="/" class="btn btn-success">На главную</a>
    """
    return HttpResponse(
        page("404 — страница не найдена", content),
        status=404,
    )
