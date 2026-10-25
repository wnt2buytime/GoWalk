"""Маршруты приложения reviews."""

from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("", views.reviews, name="list"),
    path("<int:review_id>/", views.review_detail, name="detail"),
]
