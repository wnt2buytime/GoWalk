"""Маршруты приложения routes."""

from django.urls import path

from . import views

app_name = "routes"

urlpatterns = [
    path("", views.routes, name="list"),
    path("search/", views.route_search, name="search"),
    path("<int:route_id>/", views.route_detail, name="detail"),
]
