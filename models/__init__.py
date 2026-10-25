"""Пакет моделей предметной области GoWalk."""

from .reviews import Review
from .routes import Route
from .users import User
from .waypoints import Waypoint

__all__ = ["Review", "Route", "User", "Waypoint"]
