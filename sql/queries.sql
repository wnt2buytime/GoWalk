-- ==========================================
-- GoWalk: SQL-запросы проекта
-- ==========================================
-- Каждый запрос начинается с метки "-- name: <имя>": по ней модуль
-- db/queries.py находит запрос и выполняет его из Django-представлений.
-- Значения передаются именованными параметрами (:route_id и т. п.),
-- в SQLite CLI их задают командой .param set, например:
--     .param set :route_id 1


-- name: public_routes
-- 1. Список публичных маршрутов со средней оценкой и числом отзывов
--    (выборка списка, LEFT JOIN, агрегаты AVG/COUNT, GROUP BY).
--    Страница /routes/.
SELECT
    route_details.id,
    route_details.name,
    route_details.district,
    route_details.length_km,
    route_details.difficulty,
    route_details.duration_minutes,
    route_details.author_name,
    ROUND(AVG(reviews.rating), 1) AS avg_rating,
    COUNT(reviews.id) AS reviews_count,
    (SELECT COUNT(*) FROM waypoints
     WHERE waypoints.route_id = route_details.id) AS waypoints_count
FROM route_details
LEFT JOIN reviews ON reviews.route_id = route_details.id
WHERE route_details.is_public = 1
GROUP BY route_details.id
ORDER BY route_details.name;


-- name: public_route_by_id
-- 2. Публичный маршрут по идентификатору вместе с автором и оценкой
--    (WHERE, LEFT JOIN, агрегаты). Страница /routes/<id>/.
SELECT
    route_details.*,
    ROUND(AVG(reviews.rating), 1) AS avg_rating,
    COUNT(reviews.id) AS reviews_count
FROM route_details
LEFT JOIN reviews ON reviews.route_id = route_details.id
WHERE route_details.id = :route_id
  AND route_details.is_public = 1
GROUP BY route_details.id;


-- name: route_waypoints
-- 3. Точки маршрута в порядке прохождения (WHERE, ORDER BY).
--    Страница /routes/<id>/.
SELECT
    position,
    name,
    kind
FROM waypoints
WHERE route_id = :route_id
ORDER BY position;


-- name: route_reviews
-- 4. Отзывы о маршруте с именами авторов (JOIN, WHERE).
--    Страница /routes/<id>/.
SELECT
    reviews.id,
    reviews.rating,
    reviews.rating >= 4 AS is_positive,
    reviews.text,
    strftime('%d.%m.%Y', reviews.created_at) AS created_at_display,
    users.name AS user_name
FROM reviews
JOIN users ON reviews.user_id = users.id
WHERE reviews.route_id = :route_id
ORDER BY reviews.created_at DESC;


-- name: districts
-- 5. Районы, в которых есть публичные маршруты, без повторов
--    (выборка списка, DISTINCT). Форма подбора маршрута.
SELECT DISTINCT district
FROM routes
WHERE is_public = 1
ORDER BY district;


-- name: search_routes
-- 6. Подбор маршрутов по сложности, максимальной длине и району
--    (WHERE с несколькими условиями; параметр со значением NULL
--    в отборе не участвует). Страница /routes/search/.
SELECT
    route_details.id,
    route_details.name,
    route_details.district,
    route_details.length_km,
    route_details.difficulty,
    route_details.duration_minutes,
    route_details.author_name,
    ROUND(AVG(reviews.rating), 1) AS avg_rating,
    COUNT(reviews.id) AS reviews_count,
    (SELECT COUNT(*) FROM waypoints
     WHERE waypoints.route_id = route_details.id) AS waypoints_count
FROM route_details
LEFT JOIN reviews ON reviews.route_id = route_details.id
WHERE route_details.is_public = 1
  AND (:difficulty IS NULL OR route_details.difficulty = :difficulty)
  AND (:max_length_km IS NULL OR route_details.length_km <= :max_length_km)
  AND (:district IS NULL OR route_details.district = :district)
GROUP BY route_details.id
ORDER BY route_details.length_km;


-- name: review_list
-- 7. Все отзывы о публичных маршрутах: маршрут и автор отзыва
--    (выборка списка, JOIN трёх таблиц). Страница /reviews/.
SELECT
    reviews.id,
    reviews.rating,
    reviews.rating >= 4 AS is_positive,
    reviews.text,
    strftime('%d.%m.%Y', reviews.created_at) AS created_at_display,
    routes.id AS route_id,
    routes.name AS route_name,
    users.name AS user_name
FROM reviews
JOIN routes ON reviews.route_id = routes.id
JOIN users ON reviews.user_id = users.id
WHERE routes.is_public = 1
ORDER BY reviews.created_at DESC;


-- name: review_by_id
-- 8. Отзыв по идентификатору со связанными маршрутом и автором
--    (JOIN, WHERE). Страница /reviews/<id>/.
SELECT
    reviews.id,
    reviews.rating,
    reviews.rating >= 4 AS is_positive,
    reviews.text,
    strftime('%d.%m.%Y', reviews.created_at) AS created_at_display,
    routes.id AS route_id,
    routes.name AS route_name,
    users.name AS user_name
FROM reviews
JOIN routes ON reviews.route_id = routes.id
JOIN users ON reviews.user_id = users.id
WHERE reviews.id = :review_id
  AND routes.is_public = 1;


-- name: totals
-- 9. Общие показатели сервиса (агрегаты COUNT, SUM, AVG, подзапросы).
--    Главная страница и /statistics/.
SELECT
    (SELECT COUNT(*) FROM routes WHERE is_public = 1) AS routes_count,
    (SELECT ROUND(SUM(length_km), 1) FROM routes
     WHERE is_public = 1) AS total_length_km,
    (SELECT COUNT(*) FROM reviews) AS reviews_count,
    (SELECT ROUND(AVG(rating), 2) FROM reviews) AS avg_rating,
    (SELECT COUNT(*) FROM users) AS users_count;


-- name: stats_by_district
-- 10. Маршруты по районам: количество, суммарная и средняя длина
--     (агрегаты, GROUP BY). Страница /statistics/.
SELECT
    district,
    COUNT(*) AS routes_count,
    ROUND(SUM(length_km), 1) AS total_length_km,
    ROUND(AVG(length_km), 1) AS avg_length_km
FROM routes
WHERE is_public = 1
GROUP BY district
ORDER BY routes_count DESC, district;


-- name: stats_by_difficulty
-- 11. Распределение маршрутов по сложности (GROUP BY по вычисляемому
--     полю представления). Страница /statistics/.
SELECT
    difficulty,
    COUNT(*) AS routes_count,
    CAST(ROUND(AVG(duration_minutes)) AS INTEGER) AS avg_duration_minutes
FROM route_details
WHERE is_public = 1
GROUP BY difficulty
ORDER BY MIN(length_km);


-- name: popular_routes
-- 12. Популярные маршруты: не меньше :min_reviews отзывов
--     (JOIN, GROUP BY, фильтрация групп HAVING). Страница /statistics/.
SELECT
    routes.id,
    routes.name,
    COUNT(reviews.id) AS reviews_count,
    ROUND(AVG(reviews.rating), 1) AS avg_rating
FROM routes
JOIN reviews ON reviews.route_id = routes.id
WHERE routes.is_public = 1
GROUP BY routes.id, routes.name
HAVING COUNT(reviews.id) >= :min_reviews
ORDER BY avg_rating DESC, reviews_count DESC;


-- name: author_activity
-- 13. Активность пользователей: сколько маршрутов создал и сколько
--     отзывов оставил каждый (LEFT JOIN, COUNT DISTINCT, GROUP BY).
--     Страница /statistics/.
SELECT
    users.name,
    COUNT(DISTINCT routes.id) AS routes_count,
    COUNT(DISTINCT reviews.id) AS reviews_count
FROM users
LEFT JOIN routes ON routes.author_id = users.id
LEFT JOIN reviews ON reviews.user_id = users.id
GROUP BY users.id, users.name
ORDER BY routes_count DESC, reviews_count DESC, users.name;


-- name: waypoint_kinds
-- 14. Типы точек интереса на публичных маршрутах
--     (JOIN, GROUP BY, COUNT). Страница /statistics/.
SELECT
    waypoints.kind,
    COUNT(*) AS waypoints_count
FROM waypoints
JOIN routes ON waypoints.route_id = routes.id
WHERE routes.is_public = 1
GROUP BY waypoints.kind
ORDER BY waypoints_count DESC, waypoints.kind;
