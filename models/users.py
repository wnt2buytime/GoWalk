"""Класс User и функции работы с пользователями."""


class User:
    """Пользователь сервиса: автор маршрутов и отзывов."""

    def __init__(self, user_id: int, name: str, email: str) -> None:
        """Создать объект пользователя."""
        if not User.validate_email(email):
            raise ValueError(f"Некорректный адрес почты: {email}")
        self.id = user_id
        self.name = name
        self.email = email

    @staticmethod
    def validate_email(email: str) -> bool:
        """Проверить, что адрес почты похож на корректный."""
        name, _, domain = email.partition("@")
        return bool(name) and "." in domain

    @classmethod
    def from_data(cls, data: dict) -> "User":
        """Создать пользователя из словаря с данными JSON."""
        return cls(data["id"], data["name"], data["email"])

    def to_data(self) -> dict:
        """Вернуть данные пользователя для сохранения в JSON."""
        return {"id": self.id, "name": self.name, "email": self.email}

    def __str__(self) -> str:
        """Вернуть строковое представление пользователя."""
        return f"{self.id}. {self.name} <{self.email}>"


def add_user(users: list[User], name: str, email: str) -> User:
    """Создать пользователя, добавить его в коллекцию и вернуть объект."""
    if not name.strip():
        raise ValueError("Имя пользователя не может быть пустым")
    email = email.strip().lower()
    if any(user.email == email for user in users):
        raise ValueError(f"Пользователь с почтой {email} уже есть")
    user_id = max((user.id for user in users), default=0) + 1
    user = User(user_id, name.strip(), email)
    users.append(user)
    return user


def get_user_by_id(users: list[User], user_id: int) -> User:
    """Найти пользователя по идентификатору.

    Если пользователя нет, выбрасывается LookupError.
    """
    for user in users:
        if user.id == user_id:
            return user
    raise LookupError(f"Пользователь с номером {user_id} не найден")


def find_user(users: list[User], query: str) -> list[User]:
    """Найти пользователей по подстроке в имени или адресе почты."""
    query = query.strip().lower()
    return [user for user in users
            if query in user.name.lower() or query in user.email]


def show_users(users: list[User]) -> None:
    """Вывести список пользователей."""
    if not users:
        print("Пользователи не найдены.")
    for user in users:
        print(user)
