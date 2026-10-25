"""View-функции раздела пешеходных маршрутов."""

from django.http import HttpRequest, HttpResponse
from django.utils.html import escape

from homepage.views import not_found, page
from models.reviews import get_average_rating, get_route_reviews
from models.routes import find_route_by_id, iter_public_routes
from storage import load_reviews, load_routes, load_users

DIFFICULTY_BADGES = {
    "лёгкий": "bg-success",
    "средний": "bg-warning text-dark",
    "сложный": "bg-danger",
}


def format_rating(rating: float | None) -> str:
    """Вернуть среднюю оценку в виде текста."""
    return "нет оценок" if rating is None else f"★ {rating} из 5"


def routes(request: HttpRequest) -> HttpResponse:
    """Страница со списком публичных маршрутов."""
    users = load_users()
    routes_list = load_routes(users)
    reviews = load_reviews(routes_list, users)
    rows = ""
    for route in iter_public_routes(routes_list):
        badge = DIFFICULTY_BADGES[route.difficulty]
        rating = format_rating(get_average_rating(reviews, route))
        rows += f"""
        <tr>
            <td><a href="/routes/{route.id}/">{escape(route.name)}</a></td>
            <td>{escape(route.district)}</td>
            <td>{route.length_km} км</td>
            <td><span class="badge {badge}">{route.difficulty}</span></td>
            <td>{rating}</td>
        </tr>
        """
    content = f"""
    <h1 class="mb-4">Маршруты</h1>
    <div class="table-responsive">
        <table class="table table-hover bg-white shadow-sm">
            <thead>
                <tr>
                    <th>Название</th><th>Район</th><th>Длина</th>
                    <th>Сложность</th><th>Оценка</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    """
    return HttpResponse(page("GoWalk — маршруты", content))


def route_detail(request: HttpRequest, route_id: int) -> HttpResponse:
    """Страница отдельного маршрута; скрытый маршрут не показывается."""
    users = load_users()
    routes_list = load_routes(users)
    route = find_route_by_id(routes_list, route_id)
    if route is None or not route.is_public:
        return not_found("Маршрут не найден", "/routes/", "к списку маршрутов")

    reviews = load_reviews(routes_list, users)
    route_reviews = get_route_reviews(reviews, route)
    waypoints = "".join(
        f'<li class="list-group-item">{escape(point.name)} '
        f'<span class="text-muted">({point.kind})</span></li>'
        for point in route.waypoints
    )
    review_items = "".join(
        f'<li class="list-group-item">'
        f'<a href="/reviews/{review.id}/">★ {review.rating}</a> '
        f'{escape(review.user.name)}: {escape(review.text)}</li>'
        for review in route_reviews
    ) or '<li class="list-group-item text-muted">Отзывов пока нет</li>'
    badge = DIFFICULTY_BADGES[route.difficulty]
    rating = format_rating(get_average_rating(reviews, route))
    content = f"""
    <div class="card shadow-sm mb-4">
        <div class="card-body">
            <h1 class="card-title h3">{escape(route.name)}</h1>
            <p class="card-text">
                <span class="badge {badge}">{route.difficulty}</span>
                <span class="ms-2">{rating}</span>
            </p>
            <p class="card-text"><strong>Район:</strong>
                {escape(route.district)}</p>
            <p class="card-text"><strong>Длина:</strong>
                {route.length_km} км</p>
            <p class="card-text"><strong>Набор высоты:</strong>
                {route.elevation_gain_m} м</p>
            <p class="card-text"><strong>Ожидаемая продолжительность:</strong>
                {route.duration_minutes()} мин</p>
            <p class="card-text"><strong>Автор:</strong>
                {escape(route.author.name)}</p>
            <p class="card-text"><strong>Дата создания:</strong>
                {route.created_at:%d.%m.%Y}</p>
        </div>
    </div>
    <div class="row g-4">
        <div class="col-md-6">
            <h2 class="h5">Точки маршрута</h2>
            <ol class="list-group list-group-numbered">{waypoints}</ol>
        </div>
        <div class="col-md-6">
            <h2 class="h5">Отзывы</h2>
            <ul class="list-group">{review_items}</ul>
        </div>
    </div>
    <a href="/routes/" class="btn btn-outline-secondary mt-4">
        ← к списку маршрутов
    </a>
    """
    return HttpResponse(page(escape(route.name), content))
