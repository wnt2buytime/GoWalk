"""Проверка погодных условий для прогулки."""

MIN_COMFORT_TEMPERATURE_C = -10
MAX_COMFORT_TEMPERATURE_C = 35


def is_good_weather_for_walk(
    temperature_c: float,
    is_raining: bool
) -> tuple[bool, str]:
    """Проверить, подходит ли погода для прогулки.

    Возвращает пару: признак подходящей погоды и текстовое пояснение.
    """
    if is_raining:
        return False, "Идёт дождь — прогулку лучше отложить"
    if (temperature_c < MIN_COMFORT_TEMPERATURE_C
            or temperature_c > MAX_COMFORT_TEMPERATURE_C):
        return False, "Слишком экстремальная температура для прогулки"
    return True, "Погода подходит для прогулки"
