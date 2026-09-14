from datetime import date

route_name = "Прогулка по набережной"
length_km = 4.5
elevation_gain_m = 60
avg_speed_kmh = 4.0
created_at = date(2026, 9, 14)
is_public = True


def get_difficulty_level(length_km, elevation_gain_m):
    if length_km <= 3 and elevation_gain_m <= 30:
        return "лёгкий"
    elif length_km <= 7 and elevation_gain_m <= 100:
        return "средний"
    else:
        return "сложный"


def calculate_duration_minutes(length_km, avg_speed_kmh):
    hours = length_km / avg_speed_kmh
    return round(hours * 60)


def is_good_weather_for_walk(temperature_c, is_raining):
    if is_raining:
        return False, "Идёт дождь — прогулку лучше отложить"
    if temperature_c < -10 or temperature_c > 35:
        return False, "Слишком экстремальная температура для прогулки"
    return True, "Погода подходит для прогулки"


duration_minutes = calculate_duration_minutes(length_km, avg_speed_kmh)
difficulty = get_difficulty_level(length_km, elevation_gain_m)
weather_ok, weather_message = is_good_weather_for_walk(temperature_c=18, is_raining=False)

print(f"Маршрут: {route_name}")
print(f"Длина: {length_km} км")
print(f"Набор высоты: " + str(elevation_gain_m) + " м")
print(f"Сложность: {difficulty}")
print(f"Ожидаемая продолжительность: {duration_minutes} мин")
print(f"Дата создания: {created_at}")
print(f"Публичный маршрут: {is_public}")
print(weather_message)
