-- ==========================================
-- GoWalk: структура базы данных
-- ==========================================

-- Пользователи: авторы маршрутов и отзывов.
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

-- Пешеходные маршруты. Сложность и продолжительность не хранятся,
-- а вычисляются в представлении route_details.
CREATE TABLE IF NOT EXISTS routes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    district TEXT NOT NULL,
    length_km REAL NOT NULL CHECK (length_km > 0),
    elevation_gain_m INTEGER NOT NULL DEFAULT 0
        CHECK (elevation_gain_m >= 0),
    author_id INTEGER NOT NULL,
    is_public INTEGER NOT NULL DEFAULT 1 CHECK (is_public IN (0, 1)),
    created_at TEXT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES users(id)
);

-- Точки маршрута в порядке прохождения (position).
CREATE TABLE IF NOT EXISTS waypoints (
    id INTEGER PRIMARY KEY,
    route_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    name TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'другое',
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE,
    UNIQUE (route_id, position)
);

-- Отзывы: один пользователь — один отзыв о маршруте.
-- Текст отзыва может отсутствовать (NULL): допускается только оценка.
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY,
    route_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    text TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE (route_id, user_id)
);

-- Маршрут вместе с автором и вычисляемыми полями.
-- Правило сложности совпадает с get_difficulty_level() из models/routes.py,
-- продолжительность считается при средней скорости 4 км/ч.
CREATE VIEW IF NOT EXISTS route_details AS
SELECT
    routes.id,
    routes.name,
    routes.district,
    routes.length_km,
    routes.elevation_gain_m,
    routes.is_public,
    routes.created_at,
    strftime('%d.%m.%Y', routes.created_at) AS created_at_display,
    routes.author_id,
    users.name AS author_name,
    CASE
        WHEN routes.length_km <= 3 AND routes.elevation_gain_m <= 30
            THEN 'лёгкий'
        WHEN routes.length_km <= 7 AND routes.elevation_gain_m <= 100
            THEN 'средний'
        ELSE 'сложный'
    END AS difficulty,
    CAST(ROUND(routes.length_km / 4.0 * 60) AS INTEGER) AS duration_minutes
FROM routes
JOIN users ON routes.author_id = users.id;
