"""Корневая маршрутизация проекта GoWalk."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("routes/", include("routes.urls")),
    path("reviews/", include("reviews.urls")),
]

handler404 = "homepage.views.page_not_found"
