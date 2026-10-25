"""GoWalk — консольное приложение для подбора пешеходных маршрутов."""

import inspect
from collections.abc import Callable

from reviews import (add_review, delete_route_reviews, get_average_rating,
                     get_route_reviews)
from routes import (DIFFICULTY_LEVELS, add_route, calculate_duration_minutes,
                    delete_route, filter_routes, find_routes, get_districts,
                    get_difficulty_level, get_route, iter_public_routes,
                    sort_routes)
from storage import load_reviews, load_routes, save_reviews, save_routes
from utils import (input_float, input_int, input_text, input_yes_no,
                   parse_waypoints)
from weather import is_good_weather_for_walk

SORT_OPTIONS = (
    ("name", "по названию"),
    ("length", "по длине"),
    ("difficulty", "по сложности"),
)


def format_rating(reviews: list[dict], route_id: int) -> str:
    """Вернуть среднюю оценку маршрута в виде строки."""
    rating = get_average_rating(reviews, route_id)
    return "нет оценок" if rating is None else f"{rating} из 5"


def show_route_list(route_list: list[dict], reviews: list[dict]) -> None:
    """Вывести маршруты в виде таблицы."""
    if not route_list:
        print("Маршруты не найдены.")
        return
    print(f"{'№':>3}  {'Название':<35} {'Район':<15} {'Км':>5}  "
          f"{'Сложность':<9}  Оценка")
    for route in route_list:
        difficulty = get_difficulty_level(
            route["length_km"], route["elevation_gain_m"]
        )
        print(f"{route['id']:>3}  {route['name']:<35} "
              f"{route['district']:<15} {route['length_km']:>5}  "
              f"{difficulty:<9}  {format_rating(reviews, route['id'])}")


def show_route_details(route: dict, reviews: list[dict]) -> None:
    """Вывести подробную карточку маршрута."""
    duration_minutes = calculate_duration_minutes(route["length_km"])
    difficulty = get_difficulty_level(
        route["length_km"], route["elevation_gain_m"]
    )
    print(f"Маршрут: {route['name']}")
    print(f"Район: {route['district']}")
    print(f"Длина: {route['length_km']} км")
    print("Набор высоты: " + str(route["elevation_gain_m"]) + " м")
    print(f"Сложность: {difficulty}")
    print(f"Ожидаемая продолжительность: {duration_minutes} мин")
    print(f"Точки маршрута: {' → '.join(route['waypoints'])}")
    print(f"Автор: {route['author']}")
    print(f"Дата создания: {route['created_at']}")
    print(f"Публичный маршрут: {'да' if route['is_public'] else 'нет'}")
    print(f"Средняя оценка: {format_rating(reviews, route['id'])}")


def show_routes(routes: dict[int, dict], reviews: list[dict]) -> None:
    """Показать публичные маршруты."""
    show_route_list(list(iter_public_routes(routes)), reviews)


def show_route_card(routes: dict[int, dict], reviews: list[dict]) -> None:
    """Показать карточку маршрута."""
    route_id = input_int("Номер маршрута: ")
    show_route_details(get_route(routes, route_id), reviews)


def search_routes(routes: dict[int, dict], reviews: list[dict]) -> None:
    """Найти маршрут по названию или достопримечательности."""
    query = input_text("Что ищем: ")
    show_route_list(find_routes(routes, query), reviews)


def choose_routes(routes: dict[int, dict], reviews: list[dict]) -> None:
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
    show_route_list(
        filter_routes(routes, difficulty, max_length_km, district), reviews
    )


def show_sorted_routes(routes: dict[int, dict], reviews: list[dict]) -> None:
    """Отсортировать маршруты."""
    for number, (_, title) in enumerate(SORT_OPTIONS, start=1):
        print(f"{number}. {title}")
    choice = input_int("Способ сортировки: ", 1, len(SORT_OPTIONS))
    key = SORT_OPTIONS[choice - 1][0]
    show_route_list(
        sort_routes(list(iter_public_routes(routes)), key), reviews
    )


def create_route(routes: dict[int, dict], reviews: list[dict]) -> None:
    """Добавить маршрут."""
    route = add_route(
        routes,
        name=input_text("Название: "),
        district=input_text("Район: "),
        length_km=input_float("Длина, км: ", min_value=0.1),
        elevation_gain_m=input_int("Набор высоты, м: ", min_value=0),
        waypoints=parse_waypoints(
            input_text("Точки маршрута через запятую: ")
        ),
        author=input_text("Автор: "),
        is_public=input_yes_no("Сделать маршрут публичным?"),
    )
    save_routes(routes)
    print(f"Маршрут «{route['name']}» добавлен под номером {route['id']}.")


def remove_route(routes: dict[int, dict], reviews: list[dict]) -> None:
    """Удалить маршрут."""
    route = delete_route(routes, input_int("Номер маршрута: "))
    deleted_count = delete_route_reviews(reviews, route["id"])
    save_routes(routes)
    save_reviews(reviews)
    print(f"Маршрут «{route['name']}» удалён "
          f"(удалено отзывов: {deleted_count}).")


def leave_review(routes: dict[int, dict], reviews: list[dict]) -> None:
    """Оставить отзыв о маршруте."""
    route_id = input_int("Номер маршрута: ")
    get_route(routes, route_id)
    add_review(
        reviews,
        routes,
        route_id,
        author=input_text("Ваше имя: "),
        rating=input_int("Оценка (1–5): ", 1, 5),
        text=input_text("Отзыв: ", allow_empty=True),
    )
    save_reviews(reviews)
    print("Спасибо за отзыв!")


def show_reviews(routes: dict[int, dict], reviews: list[dict]) -> None:
    """Показать отзывы о маршруте."""
    route = get_route(routes, input_int("Номер маршрута: "))
    route_reviews = get_route_reviews(reviews, route["id"])
    print(f"Отзывы о маршруте «{route['name']}» "
          f"(средняя оценка: {format_rating(reviews, route['id'])}):")
    if not route_reviews:
        print("Отзывов пока нет.")
    for review in route_reviews:
        print(f"- {review['author']}, {review['created_at']}, "
              f"оценка {review['rating']}: {review['text']}")


def check_weather(routes: dict[int, dict], reviews: list[dict]) -> None:
    """Проверить погоду для прогулки."""
    temperature_c = input_float("Температура воздуха, °C: ")
    is_raining = input_yes_no("Идёт дождь?")
    _, message = is_good_weather_for_walk(temperature_c, is_raining)
    print(message)


MENU_ACTIONS = {
    "1": show_routes,
    "2": show_route_card,
    "3": search_routes,
    "4": choose_routes,
    "5": show_sorted_routes,
    "6": create_route,
    "7": remove_route,
    "8": leave_review,
    "9": show_reviews,
    "10": check_weather,
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
        routes = load_routes()
        reviews = load_reviews()
    except ValueError as error:
        print(f"Ошибка загрузки данных: {error}")
        return

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()
        if choice == "0":
            print("До встречи на прогулке!")
            break
        action = MENU_ACTIONS.get(choice)
        if action is None:
            print("Такого пункта меню нет.")
            continue
        print()
        try:
            action(routes, reviews)
        except (ValueError, LookupError) as error:
            print(f"Ошибка: {error}")
        except OSError as error:
            print(f"Не удалось сохранить данные: {error}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nРабота программы прервана.")
