"""Вспомогательные функции ввода данных с обработкой ошибок."""


def input_text(prompt: str, allow_empty: bool = False) -> str:
    """Запросить строку; пустой ввод повторяется, если он не разрешён."""
    while True:
        text = input(prompt).strip()
        if text or allow_empty:
            return text
        print("Значение не может быть пустым.")


def input_int(
    prompt: str,
    min_value: int | None = None,
    max_value: int | None = None
) -> int:
    """Запросить целое число; при некорректном вводе повторить запрос."""
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("Введите целое число.")
            continue
        if min_value is not None and value < min_value:
            print(f"Число должно быть не меньше {min_value}.")
        elif max_value is not None and value > max_value:
            print(f"Число должно быть не больше {max_value}.")
        else:
            return value


def input_float(prompt: str, min_value: float | None = None) -> float:
    """Запросить дробное число (допускается запятая вместо точки)."""
    while True:
        try:
            value = float(input(prompt).replace(",", "."))
        except ValueError:
            print("Введите число, например 4.5.")
            continue
        if min_value is not None and value < min_value:
            print(f"Число должно быть не меньше {min_value}.")
        else:
            return value


def input_yes_no(prompt: str) -> bool:
    """Запросить ответ «да» или «нет»."""
    while True:
        answer = input(f"{prompt} (д/н): ").strip().lower()
        if answer in ("д", "да", "y", "yes"):
            return True
        if answer in ("н", "нет", "n", "no"):
            return False
        print("Ответьте «д» или «н».")


def parse_waypoints(text: str) -> list[str]:
    """Разобрать строку с точками маршрута, перечисленными через запятую."""
    return [point.strip() for point in text.split(",") if point.strip()]
