"""View-функции раздела отзывов о маршрутах."""

from django.http import HttpRequest, HttpResponse
from django.utils.html import escape

from homepage.views import not_found, page
from models.reviews import find_review_by_id
from storage import load_reviews, load_routes, load_users


def rating_badge(rating: int) -> str:
    """Вернуть HTML-бейдж оценки: зелёный для положительной."""
    color = "bg-success" if rating >= 4 else "bg-secondary"
    return f'<span class="badge {color}">★ {rating}</span>'


def reviews(request: HttpRequest) -> HttpResponse:
    """Страница со списком отзывов о публичных маршрутах."""
    users = load_users()
    routes_list = load_routes(users)
    items = ""
    for review in load_reviews(routes_list, users):
        if not review.route.is_public:
            continue
        items += f"""
        <li class="list-group-item d-flex justify-content-between">
            <a href="/reviews/{review.id}/">
                {escape(review.route.name)} — {escape(review.user.name)}
            </a>
            {rating_badge(review.rating)}
        </li>
        """
    content = f"""
    <h1 class="mb-4">Отзывы</h1>
    <ul class="list-group shadow-sm">{items}</ul>
    """
    return HttpResponse(page("GoWalk — отзывы", content))


def review_detail(request: HttpRequest, review_id: int) -> HttpResponse:
    """Страница отдельного отзыва со связанными маршрутом и автором."""
    users = load_users()
    routes_list = load_routes(users)
    review = find_review_by_id(load_reviews(routes_list, users), review_id)
    if review is None or not review.route.is_public:
        return not_found("Отзыв не найден", "/reviews/", "к списку отзывов")

    content = f"""
    <div class="card shadow-sm">
        <div class="card-body">
            <h1 class="card-title h3">Отзыв №{review.id}</h1>
            <p class="card-text"><strong>Маршрут:</strong>
                <a href="/routes/{review.route.id}/">
                    {escape(review.route.name)}</a></p>
            <p class="card-text"><strong>Автор:</strong>
                {escape(review.user.name)}</p>
            <p class="card-text"><strong>Оценка:</strong>
                {rating_badge(review.rating)}</p>
            <p class="card-text"><strong>Дата:</strong>
                {review.created_at:%d.%m.%Y}</p>
            <p class="card-text">{escape(review.text)}</p>
            <a href="/reviews/" class="btn btn-outline-secondary">
                ← к списку отзывов
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(f"Отзыв №{review.id}", content))
