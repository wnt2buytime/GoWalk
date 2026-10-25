"""View-функции раздела пешеходных маршрутов (данные из SQLite)."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.queries import fetch_all, fetch_one
from models.routes import DIFFICULTY_LEVELS


def routes(request: HttpRequest) -> HttpResponse:
    """Страница со списком публичных маршрутов и их оценками."""
    context = {
        "routes": fetch_all("public_routes"),
        "difficulty_levels": DIFFICULTY_LEVELS,
    }
    return render(request, "routes/route_list.html", context)


def route_detail(request: HttpRequest, route_id: int) -> HttpResponse:
    """Страница отдельного маршрута; скрытый маршрут не показывается."""
    params = {"route_id": route_id}
    route = fetch_one("public_route_by_id", params)
    context = {"route": route}
    if route is not None:
        context["waypoints"] = fetch_all("route_waypoints", params)
        context["reviews"] = fetch_all("route_reviews", params)
    return render(
        request,
        "routes/route_detail.html",
        context,
        status=404 if route is None else 200,
    )


def parse_max_length(value: str) -> float | None:
    """Преобразовать введённую длину в число; пустое значение — None.

    При некорректном вводе выбрасывается ValueError.
    """
    value = value.strip().replace(",", ".")
    if not value:
        return None
    length = float(value)
    if length <= 0:
        raise ValueError("Длина должна быть больше нуля")
    return length


def route_search(request: HttpRequest) -> HttpResponse:
    """Подбор маршрута по сложности, максимальной длине и району."""
    difficulty = request.GET.get("difficulty") or None
    district = request.GET.get("district") or None
    max_length_text = request.GET.get("max_length_km", "")
    context = {
        "difficulty_levels": DIFFICULTY_LEVELS,
        "districts": fetch_all("districts"),
        "difficulty": difficulty,
        "district": district,
        "max_length_text": max_length_text,
        "is_submitted": bool(request.GET),
        "routes": [],
    }
    if difficulty is not None and difficulty not in DIFFICULTY_LEVELS:
        context["error"] = "Неизвестный уровень сложности."
    else:
        try:
            max_length_km = parse_max_length(max_length_text)
        except ValueError:
            context["error"] = "Длина должна быть числом больше 0."
        else:
            if context["is_submitted"]:
                context["routes"] = fetch_all("search_routes", {
                    "difficulty": difficulty,
                    "max_length_km": max_length_km,
                    "district": district,
                })
    return render(request, "routes/route_search.html", context)
