"""Тесты веб-страниц на данных из каталога data/."""

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


def test_routes_page_shows_only_public_routes(client):
    routes = load_routes(load_users())
    response = client.get("/routes/")
    shown = [route for route, _ in response.context["routes_with_ratings"]]
    assert response.status_code == 200
    assert "routes/includes/route_card.html" in template_names(response)
    assert all(route.is_public for route in shown)
    assert len(shown) == sum(route.is_public for route in routes)


def test_route_detail_page(client):
    response = client.get("/routes/1/")
    assert response.status_code == 200
    assert response.context["route"].id == 1
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
    detail = client.get(f"/reviews/{review.id}/")
    assert detail.status_code == 200
    assert review.route.name in detail.content.decode()


@override_settings(DEBUG=False)
def test_custom_404_page(client):
    response = client.get("/nonexistent/")
    assert response.status_code == 404
    assert "404.html" in template_names(response)
