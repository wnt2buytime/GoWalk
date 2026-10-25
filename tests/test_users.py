import pytest

from models import User, Waypoint
from models.users import add_user, find_user, get_user_by_id


def test_user_creation():
    user = User(1, "Анна", "anna@example.com")
    assert user.id == 1
    assert user.name == "Анна"
    assert user.email == "anna@example.com"
    assert str(user) == "1. Анна <anna@example.com>"


def test_user_from_data():
    user = User.from_data(
        {"id": 2, "name": "Олег", "email": "oleg@example.com"}
    )
    assert user.id == 2
    assert user.to_data()["email"] == "oleg@example.com"


def test_user_with_invalid_email():
    assert not User.validate_email("anna.example.com")
    with pytest.raises(ValueError):
        User(1, "Анна", "anna@")


def test_add_and_find_user():
    users = []
    add_user(users, "Анна", "Anna@Example.com")
    add_user(users, "Олег", "oleg@example.com")
    assert get_user_by_id(users, 2).name == "Олег"
    assert [user.id for user in find_user(users, "anna@")] == [1]


def test_add_user_with_duplicate_email():
    users = []
    add_user(users, "Анна", "anna@example.com")
    with pytest.raises(ValueError):
        add_user(users, "Анна 2", "anna@example.com")


def test_waypoint():
    waypoint = Waypoint("Музеон", "парк")
    assert waypoint.matches("музе")
    assert str(waypoint) == "Музеон (парк)"
    with pytest.raises(ValueError):
        Waypoint("Музеон", "космодром")
