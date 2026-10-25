"""Тесты веб-страниц на тестовой базе SQLite (см. conftest.py)."""

import pytest
from django.test.utils import override_settings

from storage import load_routes, load_users


def template_names(response) -> list[str]:
    return [template.name for template in response.templates]


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "homepage/index.html" in template_names(response)
    assert "base.html" in template_names(response)
    assert "includes/navigation.html" in template_names(response)
    assert response.context["totals"]["routes_count"] > 0


def test_routes_page_shows_only_public_routes(client):
    routes = load_routes(load_users())
    response = client.get("/routes/")
    shown_ids = {row["id"] for row in response.context["routes"]}
    assert response.status_code == 200
    assert "routes/includes/route_card.html" in template_names(response)
    assert shown_ids == {route.id for route in routes if route.is_public}


def test_route_detail_page(client):
    response = client.get("/routes/1/")
    assert response.status_code == 200
    assert response.context["route"]["id"] == 1
    assert len(response.context["waypoints"]) > 0
    assert "Прогулка по набережной" in response.content.decode()


@pytest.mark.parametrize("url", ["/routes/999/", "/reviews/999/"])
def test_missing_object_returns_404(client, url):
    response = client.get(url)
    assert response.status_code == 404
    assert "не найден" in response.content.decode()


def test_private_route_is_hidden(client):
    private = [route for route in load_routes(load_users())
               if not route.is_public]
    for route in private:
        assert client.get(f"/routes/{route.id}/").status_code == 404


def test_reviews_pages(client):
    response = client.get("/reviews/")
    assert response.status_code == 200
    review = response.context["reviews"][0]
    detail = client.get(f"/reviews/{review['id']}/")
    assert detail.status_code == 200
    assert review["route_name"] in detail.content.decode()


def test_route_search_form_and_results(client):
    form = client.get("/routes/search/")
    assert form.status_code == 200
    assert form.context["routes"] == []

    response = client.get(
        "/routes/search/",
        {"difficulty": "лёгкий", "max_length_km": "3,5", "district": ""},
    )
    routes = response.context["routes"]
    assert routes
    assert all(row["difficulty"] == "лёгкий" for row in routes)


@pytest.mark.parametrize("params", [
    {"max_length_km": "abc"},
    {"max_length_km": "-1"},
    {"difficulty": "экстремальный"},
])
def test_route_search_invalid_input(client, params):
    response = client.get("/routes/search/", params)
    assert response.status_code == 200
    assert "error" in response.context


def test_statistics_page(client):
    response = client.get("/statistics/")
    assert response.status_code == 200
    assert "homepage/statistics.html" in template_names(response)
    assert response.context["by_district"]
    assert all(row["reviews_count"] >= response.context["popular_min_reviews"]
               for row in response.context["popular_routes"])


@override_settings(DEBUG=False)
def test_custom_404_page(client):
    response = client.get("/nonexistent/")
    assert response.status_code == 404
    assert "404.html" in template_names(response)
