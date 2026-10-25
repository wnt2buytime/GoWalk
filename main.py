"""GoWalk — консольное приложение для подбора пешеходных маршрутов."""

import inspect
from collections.abc import Callable

from models import Review, Route, User, Waypoint
from models.reviews import (add_review, delete_route_reviews,
                            get_average_rating, get_ratings,
                            get_route_reviews, show_reviews)
from models.routes import (DIFFICULTY_LEVELS, add_route, delete_route,
                           filter_routes, find_routes, get_districts,
                           get_route_by_id, iter_public_routes,
                           show_route_details, show_routes, sort_routes)
from models.users import add_user, find_user, get_user_by_id, show_users
from models.waypoints import WAYPOINT_KINDS
from storage import (load_reviews, load_routes, load_users, save_reviews,
                     save_routes, save_users)
from utils import input_float, input_int, input_text, input_yes_no
from weather import is_good_weather_for_walk

SORT_OPTIONS = (
    ("name", "по названию"),
    ("length", "по длине"),
    ("difficulty", "по сложности"),
)


def save_data(
    routes: list[Route],
    users: list[User],
    reviews: list[Review]
) -> None:
    """Сохранить все коллекции объектов в JSON-файлы."""
    save_users(users)
    save_routes(routes)
    save_reviews(reviews)


def choose_route(routes: list[Route]) -> Route:
    """Запросить номер маршрута и вернуть найденный объект."""
    return get_route_by_id(routes, input_int("Номер маршрута: "))


def choose_user(users: list[User]) -> User:
    """Запросить номер пользователя и вернуть найденный объект."""
    return get_user_by_id(users, input_int("Номер пользователя: "))


def input_waypoint() -> Waypoint | None:
    """Запросить точку маршрута; пустое название завершает ввод."""
    name = input_text("Название точки (пусто — закончить): ",
                      allow_empty=True)
    if not name:
        return None
    for number, kind in enumerate(WAYPOINT_KINDS, start=1):
        print(f"  {number}. {kind}")
    kind_number = input_int("Тип точки: ", 1, len(WAYPOINT_KINDS))
    return Waypoint(name, WAYPOINT_KINDS[kind_number - 1])


def show_public_routes(
    routes: list[Route],
    users: list[User],
    reviews: list[Review]
) -> None:
    """Показать публичные маршруты."""
    public_routes = list(iter_public_routes(routes))
    show_routes(public_routes, get_ratings(reviews, public_routes))


def show_route_card(
    routes: list[Route],
    users: list[User],
    reviews: list[Review]
) -> None:
    """Показать карточку маршрута."""
    route = choose_route(routes)
    show_route_details(route)
    rating = get_average_rating(reviews, route)
    print(f"Средняя оценка: {'нет оценок' if rating is None else rating}")


def search_routes(
    routes: list[Route],
    users: list[User],
    reviews: list[Review]
) -> None:
    """Найти маршрут по названию или достопримечательности."""
    found = find_routes(routes, input_text("Что ищем: "))
    show_routes(found, get_ratings(reviews, found))


def choose_routes(
    routes: list[Route],
    users: list[User],
    reviews: list[Review]
) -> None:
    """Подобрать маршрут по параметрам."""
    print("Сложность: " + ", ".join(DIFFICULTY_LEVELS)
          + " (пусто — любая)")
    difficulty = input_text("Сложность: ", allow_empty=True).lower() or None
    if difficulty is not None and difficulty not in DIFFICULTY_LEVELS:
        raise ValueError(f"Неизвестная сложность: {difficulty}")

    max_length_km = None
    if input_yes_no("Ограничить длину маршрута?"):
        max_length_km = input_float("Максимальная длина, км: ", min_value=0)

    print("Районы: " + ", ".join(get_districts(routes)) + " (пусто — любой)")
    district = input_text("Район: ", allow_empty=True) or None
    found = filter_routes(routes, difficulty, max_length_km, district)
    show_routes(found, get_ratings(reviews, found))


def show_sorted_routes(
    routes: list[Route],
    users: list[User],
    reviews: list[Review]
) -> None:
    """Отсортировать маршруты."""
    for number, (_, title) in enumerate(SORT_OPTIONS, start=1):
        print(f"{number}. {title}")
    choice = input_int("Способ сортировки: ", 1, len(SORT_OPTIONS))
    key = SORT_OPTIONS[choice - 1][0]
    sorted_routes = sort_routes(list(iter_public_routes(routes)), key)
    show_routes(sorted_routes, get_ratings(reviews, sorted_routes))


def create_route(
    routes: list[Route],
    users: list[User],
    reviews: list[Review]
) -> None:
    """Добавить маршрут."""
    author = choose_user(users)
    name = input_text("Название: ")
    district = input_text("Район: ")
    length_km = input_float("Длина, км: ", min_value=0.1)
    elevation_gain_m = input_int("Набор высоты, м: ", min_value=0)
    waypoints = []
    while (waypoint := input_waypoint()) is not None:
        waypoints.append(waypoint)
    is_public = input_yes_no("Сделать маршрут публичным?")
    route = add_route(routes, name, district, length_km, elevation_gain_m,
                      author, waypoints, is_public)
    save_data(routes, users, reviews)
    print(f"Маршрут «{route.name}» добавлен под номером {route.id}.")


def extend_route(
    routes: list[Route],
    users: list[User],
    reviews: list[Review]
) -> None:
    """Добавить точку в маршрут."""
    route = choose_route(routes)
    waypoint = input_waypoint()
    if waypoint is None:
        print("Точка не добавлена.")
        return
    route.add_waypoint(waypoint)
    save_data(routes, users, reviews)
    print(f"Точка «{waypoint.name}» добавлена в маршрут «{route.name}».")


def remove_route(
    routes: list[Route],
    users: list[User],
    reviews: list[Review]
) -> None:
    """Удалить маршрут."""
    route = delete_route(routes, input_int("Номер маршрута: "))
    deleted_count = delete_route_reviews(reviews, route)
    save_data(routes, users, reviews)
    print(f"Маршрут «{route.name}» удалён "
          f"(удалено отзывов: {deleted_count}).")


def leave_review(
    routes: list[Route],
    users: list[User],
    reviews: list[Review]
) -> None:
    """Оставить отзыв о маршруте."""
    route = choose_route(routes)
    user = choose_user(users)
    rating = input_int("Оценка (1–5): ", 1, 5)
    text = input_text("Отзыв: ", allow_empty=True)
    review = add_review(reviews, route, user, rating, text)
    if review is None:
        print(f"{user.name} уже оставлял(а) отзыв о маршруте «{route.name}».")
        return
    save_data(routes, users, reviews)
    print(f"Спасибо за отзыв! Номер отзыва: {review.id}.")


def show_route_reviews(
    routes: list[Route],
    users: list[User],
    reviews: list[Review]
) -> None:
    """Показать отзывы о маршруте."""
    route = choose_route(routes)
    print(f"Отзывы о маршруте «{route.name}»:")
    show_reviews(get_route_reviews(reviews, route))


def show_all_users(
    routes: list[Route],
    users: list[User],
    reviews: list[Review]
) -> None:
    """Показать пользователей."""
    query = input_text("Поиск по имени или почте (пусто — все): ",
                       allow_empty=True)
    show_users(find_user(users, query) if query else users)


def register_user(
    routes: list[Route],
    users: list[User],
    reviews: list[Review]
) -> None:
    """Зарегистрировать пользователя."""
    user = add_user(users, input_text("Имя: "), input_text("Почта: "))
    save_data(routes, users, reviews)
    print(f"Пользователь {user} зарегистрирован.")


def check_weather(
    routes: list[Route],
    users: list[User],
    reviews: list[Review]
) -> None:
    """Проверить погоду для прогулки."""
    temperature_c = input_float("Температура воздуха, °C: ")
    is_raining = input_yes_no("Идёт дождь?")
    _, message = is_good_weather_for_walk(temperature_c, is_raining)
    print(message)


MENU_ACTIONS = {
    "1": show_public_routes,
    "2": show_route_card,
    "3": search_routes,
    "4": choose_routes,
    "5": show_sorted_routes,
    "6": create_route,
    "7": extend_route,
    "8": remove_route,
    "9": leave_review,
    "10": show_route_reviews,
    "11": show_all_users,
    "12": register_user,
    "13": check_weather,
}


def get_action_title(action: Callable) -> str:
    """Получить название пункта меню из документации функции."""
    return inspect.getdoc(action).splitlines()[0].rstrip(".")


def print_menu() -> None:
    """Вывести меню приложения."""
    print("\n=== GoWalk — пешеходные маршруты ===")
    for key, action in MENU_ACTIONS.items():
        print(f"{key}. {get_action_title(action)}")
    print("0. Выход")


def main() -> None:
    """Точка запуска приложения: загрузка данных и цикл меню."""
    try:
        users = load_users()
        routes = load_routes(users)
        reviews = load_reviews(routes, users)
    except ValueError as error:
        print(f"Ошибка загрузки данных: {error}")
        return

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()
        if choice == "0":
            break
        action = MENU_ACTIONS.get(choice)
        if action is None:
            print("Такого пункта меню нет.")
            continue
        print()
        try:
            action(routes, users, reviews)
        except (ValueError, LookupError) as error:
            print(f"Ошибка: {error}")
        except OSError as error:
            print(f"Не удалось сохранить данные: {error}")

    try:
        save_data(routes, users, reviews)
    except OSError as error:
        print(f"Не удалось сохранить данные: {error}")
    print("До встречи на прогулке!")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nРабота программы прервана.")
