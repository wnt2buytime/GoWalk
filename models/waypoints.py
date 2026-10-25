"""Класс Waypoint — точка маршрута."""

WAYPOINT_KINDS = ("достопримечательность", "парк", "набережная",
                  "смотровая площадка", "музей", "транспорт", "другое")


class Waypoint:
    """Точка интереса, через которую проходит маршрут."""

    def __init__(self, name: str, kind: str = "другое") -> None:
        """Создать точку маршрута."""
        if not name.strip():
            raise ValueError("Название точки не может быть пустым")
        if kind not in WAYPOINT_KINDS:
            raise ValueError(f"Неизвестный тип точки: {kind}")
        self.name = name.strip()
        self.kind = kind

    def matches(self, query: str) -> bool:
        """Проверить, встречается ли подстрока в названии точки."""
        return query.lower() in self.name.lower()

    @classmethod
    def from_data(cls, data: dict) -> "Waypoint":
        """Создать точку маршрута из словаря с данными JSON."""
        return cls(data["name"], data.get("kind", "другое"))

    def to_data(self) -> dict:
        """Вернуть данные точки для сохранения в JSON."""
        return {"name": self.name, "kind": self.kind}

    def __str__(self) -> str:
        """Вернуть строковое представление точки маршрута."""
        return f"{self.name} ({self.kind})"
