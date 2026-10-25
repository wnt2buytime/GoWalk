# GoWalk

## Назначение

GoWalk — сервис для создания и подбора пешеходных прогулочных маршрутов
по городу. Пользователь может создавать собственные маршруты, указывая
точки интереса, длину и сложность, а также просматривать и оценивать
маршруты, созданные другими пользователями.

Консольная версия приложения (ПР1–ПР3) дополнена веб-интерфейсом
на Django (ПР5), страницы которого с ПР6 формируются шаблонами Django,
а с ПР7 получают данные из базы данных SQLite SQL-запросами.

## Используемые технологии

- Python 3.12;
- Django 5.2 — веб-фреймворк;
- Django Template Language — шаблоны страниц;
- HTML5 — разметка страниц;
- CSS3 и Bootstrap 5.3 — оформление страниц;
- JavaScript — небольшое поведение интерфейса;
- SQLite и SQL — база данных веб-версии (модуль `sqlite3`);
- JSON — хранение данных консольной версии и источник импорта;
- pytest — автоматизированные тесты;
- flake8 — проверка качества кода.

## Целевая аудитория

Жители и гости города, которые хотят провести время на свежем воздухе:
любители пеших прогулок, туристы, семьи с детьми, люди, восстанавливающие
физическую форму после травм и ищущие маршруты подходящей сложности.

## Предметная область

Сервис планирования пеших прогулок в городской среде. Приложение хранит
маршруты, состоящие из точек интереса, с привязкой к пользователям,
которые эти маршруты создают, проходят и оценивают.

## Основные сущности (классы)

Начиная с ПР3 сущности предметной области представлены классами
пакета `models`, а данные — объектами этих классов.

### User — пользователь

- Атрибуты: `id`, `name`, `email`.
- Методы: `from_data()` (`@classmethod`) — создание из словаря JSON;
  `validate_email()` (`@staticmethod`) — проверка адреса почты;
  `to_data()`; `__str__()`.

### Waypoint — точка маршрута

- Атрибуты: `name`, `kind` (парк, музей, набережная и т. п.).
- Методы: `matches()` — поиск по названию; `from_data()`
  (`@classmethod`); `to_data()`; `__str__()`.

### Route — маршрут

- Атрибуты: `id`, `name`, `district`, `length_km`, `elevation_gain_m`,
  `author` (объект `User`), `waypoints` (список объектов `Waypoint`),
  `is_public`, `created_at`.
- Методы: `difficulty` (`@property`) — сложность по длине и набору
  высоты; `duration_minutes()` — продолжительность прогулки;
  `add_waypoint()` — добавление точки; `matches()` — поиск по названию
  и точкам; `validate_length()` (`@staticmethod`); `__str__()`.

### Review — отзыв о маршруте

- Атрибуты: `id`, `route` (объект `Route`), `user` (объект `User`),
  `rating`, `text`, `created_at`.
- Методы: `is_positive()` — положительный ли отзыв;
  `validate_rating()` (`@staticmethod`); `__str__()`.

## Взаимодействие объектов

Объекты хранят ссылки на связанные объекты (композиция), а не их
идентификаторы, поэтому данные доступны напрямую: `route.author.name`,
`review.route.name`, `review.user.email`.

```text
User ──автор──> Route ──содержит──> Waypoint
  │               ▲
  └──пишет──> Review
```

Правило предметной области: пользователь может оставить только один
отзыв о маршруте — повторный отзыв не создаётся (`add_review()`
возвращает `None`).

## Основные функции

- регистрация, просмотр и поиск пользователей;
- просмотр списка публичных маршрутов и карточки маршрута;
- поиск маршрутов по названию или точке интереса;
- подбор маршрутов по сложности, максимальной длине и району;
- сортировка маршрутов по названию, длине и сложности;
- создание и удаление маршрутов, добавление точек в маршрут;
- расчёт длины, продолжительности и уровня сложности маршрута;
- проверка погодных условий для комфортной прогулки;
- отзывы и оценки маршрутов, расчёт средней оценки.

## Страницы веб-интерфейса

| URL | Имя маршрута | View-функция | Шаблон | SQL-запросы |
|---|---|---|---|---|
| `/` | `homepage:index` | `index()` | `homepage/index.html` | `totals` |
| `/routes/` | `routes:list` | `routes()` | `routes/route_list.html` | `public_routes` |
| `/routes/search/` | `routes:search` | `route_search()` | `routes/route_search.html` | `districts`, `search_routes` |
| `/routes/<int:route_id>/` | `routes:detail` | `route_detail()` | `routes/route_detail.html` | `public_route_by_id`, `route_waypoints`, `route_reviews` |
| `/reviews/` | `reviews:list` | `reviews()` | `reviews/review_list.html` | `review_list` |
| `/reviews/<int:review_id>/` | `reviews:detail` | `review_detail()` | `reviews/review_detail.html` | `review_by_id` |
| `/statistics/` | `homepage:statistics` | `statistics()` | `homepage/statistics.html` | `totals`, `stats_by_district`, `stats_by_difficulty`, `popular_routes`, `author_activity`, `waypoint_kinds` |

View-функции выполняют SQL-запросы, получают строки `sqlite3.Row`
(поля доступны по именам: `{{ route.name }}`) и передают их в шаблон
через контекст функцией `render()`.

Подбор маршрута (`/routes/search/`) — форма GET с полями сложности,
максимальной длины и района. Введённые значения передаются в запрос
только как параметры; некорректная длина или неизвестная сложность
выводят сообщение об ошибке, а не роняют страницу.

Если маршрут или отзыв не найден (или маршрут скрыт автором), запрос
возвращает пустой результат: шаблон через `{% if %}` / `{% else %}`
выводит сообщение «не найден», а ответ возвращается с кодом 404.
Несуществующие адреса обрабатывает `handler404`
(`homepage.views.page_not_found()`, шаблон `templates/404.html`),
он работает при `DEBUG = False`.

## База данных (SQLite)

Файл базы — `data/gowalk.sqlite` (в Git не хранится, создаётся
скриптом импорта из JSON).

### Таблицы

**users** — пользователи

| Поле | Тип | Ограничения |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY |
| `name` | TEXT | NOT NULL |
| `email` | TEXT | NOT NULL, UNIQUE |

**routes** — маршруты

| Поле | Тип | Ограничения |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY |
| `name` | TEXT | NOT NULL |
| `district` | TEXT | NOT NULL |
| `length_km` | REAL | NOT NULL, CHECK > 0 |
| `elevation_gain_m` | INTEGER | NOT NULL, DEFAULT 0, CHECK ≥ 0 |
| `author_id` | INTEGER | NOT NULL, FOREIGN KEY → `users.id` |
| `is_public` | INTEGER | NOT NULL, DEFAULT 1, 0 или 1 |
| `created_at` | TEXT | NOT NULL, дата `YYYY-MM-DD` |

**waypoints** — точки маршрута

| Поле | Тип | Ограничения |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY |
| `route_id` | INTEGER | NOT NULL, FOREIGN KEY → `routes.id`, ON DELETE CASCADE |
| `position` | INTEGER | NOT NULL, порядок точки; UNIQUE (`route_id`, `position`) |
| `name` | TEXT | NOT NULL |
| `kind` | TEXT | NOT NULL, DEFAULT 'другое' |

**reviews** — отзывы

| Поле | Тип | Ограничения |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY |
| `route_id` | INTEGER | NOT NULL, FOREIGN KEY → `routes.id`, ON DELETE CASCADE |
| `user_id` | INTEGER | NOT NULL, FOREIGN KEY → `users.id` |
| `rating` | INTEGER | NOT NULL, CHECK 1–5 |
| `text` | TEXT | может быть NULL — отзыв только с оценкой |
| `created_at` | TEXT | NOT NULL |

Ограничение UNIQUE (`route_id`, `user_id`) не даёт пользователю оставить
второй отзыв о том же маршруте — то же правило, что в `add_review()`.

Связи: пользователь → много маршрутов (`routes.author_id`), маршрут →
много точек (`waypoints.route_id`) и отзывов (`reviews.route_id`),
пользователь → много отзывов (`reviews.user_id`).

Представление (VIEW) **route_details** добавляет к маршруту имя автора
и вычисляемые поля `difficulty`, `duration_minutes` и
`created_at_display`. Правило сложности совпадает с
`get_difficulty_level()`, совпадение проверяется тестом.

### Файлы

- `sql/schema.sql` — команды `CREATE TABLE` и `CREATE VIEW`;
- `sql/queries.sql` — 14 SQL-запросов проекта с комментариями;
- `db/database.py` — `get_connection()` (включает `PRAGMA foreign_keys
  = ON` и `row_factory = sqlite3.Row`) и `create_schema()`;
- `db/import_json.py` — перенос данных из JSON (`executemany()`,
  параметры `?`, `commit()` / `rollback()`); скрипт можно запускать
  повторно — таблицы заполняются заново;
- `db/queries.py` — загрузка запросов из `sql/queries.sql` по меткам
  `-- name:` и функции `fetch_all()` / `fetch_one()` для представлений.

### SQL-запросы (`sql/queries.sql`)

| № | Имя | Назначение | Конструкции |
|---|---|---|---|
| 1 | `public_routes` | список публичных маршрутов с оценкой | выборка, LEFT JOIN, AVG, COUNT, GROUP BY |
| 2 | `public_route_by_id` | маршрут по идентификатору | WHERE, LEFT JOIN, AVG |
| 3 | `route_waypoints` | точки маршрута по порядку | WHERE, ORDER BY |
| 4 | `route_reviews` | отзывы о маршруте с авторами | JOIN, WHERE |
| 5 | `districts` | районы без повторов | выборка, DISTINCT |
| 6 | `search_routes` | подбор по сложности, длине, району | WHERE (несколько условий), LEFT JOIN, GROUP BY |
| 7 | `review_list` | все отзывы с маршрутом и автором | выборка, JOIN трёх таблиц |
| 8 | `review_by_id` | отзыв по идентификатору | JOIN, WHERE |
| 9 | `totals` | общие показатели | COUNT, SUM, AVG, подзапросы |
| 10 | `stats_by_district` | маршруты по районам | COUNT, SUM, AVG, GROUP BY |
| 11 | `stats_by_difficulty` | маршруты по сложности | COUNT, AVG, GROUP BY |
| 12 | `popular_routes` | маршруты с N и более отзывами | JOIN, GROUP BY, HAVING |
| 13 | `author_activity` | маршруты и отзывы пользователей | LEFT JOIN, COUNT DISTINCT, GROUP BY |
| 14 | `waypoint_kinds` | точки интереса по типам | JOIN, COUNT, GROUP BY |

Значения передаются именованными параметрами (`:route_id`,
`:difficulty` и т. п.), пользовательский ввод никогда не подставляется
в текст запроса. Проверка запроса в SQLite CLI:

```text
sqlite3 data/gowalk.sqlite
sqlite> .param set :route_id 1
sqlite> SELECT position, name, kind FROM waypoints
   ...> WHERE route_id = :route_id ORDER BY position;
```

## Шаблоны (Django Template Language)

- **Базовый шаблон** `templates/base.html` — HTML-каркас, Bootstrap,
  собственные CSS и JavaScript, подвал; блоки `{% block title %}` и
  `{% block content %}`. Все страницы наследуют его через
  `{% extends "base.html" %}`.
- **Включаемые шаблоны** (`{% include %}`):
  - `templates/includes/navigation.html` — шапка с логотипом и меню;
  - `routes/includes/route_card.html` — карточка маршрута в списке;
  - `routes/includes/difficulty_badge.html` — бейдж сложности;
  - `reviews/includes/rating_badge.html` — бейдж оценки отзыва.
- **Контекст** — например, `{"routes": fetch_all("public_routes"),
  "difficulty_levels": DIFFICULTY_LEVELS}` для списка маршрутов.
- **Циклы и условия** — `{% for route in routes %}`
  с `{% empty %}`, `{% if route.difficulty == "лёгкий" %}`,
  `{% if review.is_positive %}`.
- **Именованные URL и пространства имён** — `app_name` в `urls.py`
  каждого приложения, ссылки только через `{% url 'routes:detail'
  route.id %}`.
- **Фильтры** — `length` (количество маршрутов, точек, отзывов),
  `default` (пустое название или текст отзыва), `date:"d.m.Y"` (даты),
  `floatformat:1` (средняя оценка), `truncatechars` (превью отзыва),
  `capfirst` (кнопки сложности). Фильтры только оформляют данные, бизнес-
  логика остаётся в классах ПР3.

## Статические файлы

Каталог `homepage/static/homepage/`, подключение через `{% load static %}`
и `{% static '...' %}` в `base.html` и `navigation.html`:

- `css/style.css` — собственные стили: шапка, карточки маршрутов,
  бейджи сложности, «путь» из точек маршрута, подвал;
- `js/main.js` — текущий год в подвале и быстрый отбор карточек
  маршрутов по сложности без перезагрузки страницы;
- `img/logo.svg` — логотип GoWalk в шапке и иконка вкладки.

## Структура проекта

```text
GoWalk/
├── README.md
├── requirements.txt
├── setup.cfg           настройки flake8 и pytest
├── manage.py           управление Django-проектом
├── sql/
│   ├── schema.sql      структура базы данных
│   └── queries.sql     SQL-запросы проекта
├── db/                 работа с SQLite
│   ├── __init__.py
│   ├── database.py     подключение и создание схемы
│   ├── import_json.py  перенос данных из JSON
│   └── queries.py      выполнение запросов из queries.sql
├── main.py             консольная версия: меню и сценарии
├── storage.py          загрузка и сохранение данных (JSON ↔ объекты)
├── utils.py            консольный ввод с обработкой ошибок
├── weather.py          проверка погодных условий
├── gowalk/             пакет настроек Django-проекта
│   ├── settings.py
│   ├── urls.py         корневая маршрутизация и handler404
│   ├── asgi.py
│   └── wsgi.py
├── templates/          шаблоны уровня проекта
│   ├── base.html
│   ├── 404.html
│   └── includes/
│       └── navigation.html
├── homepage/           приложение главной страницы
│   ├── static/homepage/
│   │   ├── css/style.css
│   │   ├── js/main.js
│   │   └── img/logo.svg
│   ├── templates/homepage/
│   │   ├── index.html
│   │   └── statistics.html
│   ├── urls.py
│   └── views.py        index(), statistics(), page_not_found()
├── routes/             приложение маршрутов
│   ├── templates/routes/
│   │   ├── route_list.html
│   │   ├── route_search.html
│   │   ├── route_detail.html
│   │   └── includes/
│   │       ├── route_card.html
│   │       └── difficulty_badge.html
│   ├── urls.py
│   └── views.py        routes(), route_search(), route_detail()
├── reviews/            приложение отзывов
│   ├── templates/reviews/
│   │   ├── review_list.html
│   │   ├── review_detail.html
│   │   └── includes/
│   │       └── rating_badge.html
│   ├── urls.py
│   └── views.py        reviews(), review_detail()
├── models/             классы предметной области (ПР3)
│   ├── __init__.py
│   ├── users.py
│   ├── waypoints.py
│   ├── routes.py
│   └── reviews.py
├── data/               JSON-файлы данных и база SQLite
│   ├── users.json
│   ├── routes.json
│   ├── reviews.json
│   └── gowalk.sqlite   создаётся python -m db.import_json
└── tests/              автоматизированные тесты pytest
```

Отдельное приложение для пользователей не создаётся: в Django есть
встроенная модель пользователя (`django.contrib.auth`), она понадобится
при реализации регистрации и входа.

## Хранение данных

Веб-версия читает данные из базы SQLite (раздел «База данных»).
Консольная версия и скрипт импорта работают с JSON-файлами каталога
`data/` — они остаются исходными данными проекта. При загрузке они
преобразуются в объекты `User`, `Route` и `Review`, при сохранении —
обратно в словари. Преобразование выполняет модуль `storage.py`.
Связанные объекты в JSON хранятся через идентификаторы, при загрузке
по ним находятся нужные объекты. Сложность и продолжительность маршрута
не хранятся, а вычисляются.

`data/routes.json`:

```json
{
    "id": 1,
    "name": "Прогулка по набережной",
    "district": "Хамовники",
    "length_km": 4.5,
    "elevation_gain_m": 60,
    "author_id": 1,
    "waypoints": [{"name": "Музеон", "kind": "парк"}],
    "is_public": true,
    "created_at": "2026-09-14"
}
```

`data/reviews.json`:

```json
{
    "id": 1,
    "route_id": 1,
    "user_id": 2,
    "rating": 5,
    "text": "Красивые виды на реку.",
    "created_at": "2026-09-16"
}
```

`data/users.json`:

```json
{"id": 1, "name": "Никита", "email": "nikita@example.com"}
```

## Требования

- Python 3.10+;
- Django 5.2;
- pytest;
- flake8.

Установка зависимостей:

```bash
pip install -r requirements.txt
```

## Запуск программы

Веб-версия (Django):

```bash
python -m db.import_json      # создать базу SQLite из JSON
python manage.py migrate      # служебные таблицы Django
python manage.py runserver
```

После запуска открыть в браузере http://127.0.0.1:8000/.

Консольная версия работает с JSON-файлами:

```bash
python main.py
```

Изменения, сделанные в консольной версии, попадают на сайт после
повторного импорта: `python -m db.import_json`.

## Запуск тестов

```bash
pytest -v
```

Тесты проверяют создание объектов и их методы, операции с маршрутами,
пользователями и отзывами, связи между объектами и их восстановление
при загрузке из JSON. Тесты `tests/test_views.py` запрашивают страницы
тестовым клиентом Django (настройка в `tests/conftest.py`) и проверяют
коды ответа, используемые шаблоны и контекст. Тесты `tests/test_db.py`
проверяют схему, импорт, внешние ключи, ограничения и SQL-запросы.
Для тестов `tests/conftest.py` создаёт временную базу SQLite из JSON,
поэтому рабочая база `data/gowalk.sqlite` для них не нужна.

## Проверка качества кода

```bash
flake8
```

## Текущее состояние и план развития

Реализовано:

- ПР1 — начальный сценарий: сложность, продолжительность, погода;
- ПР2 — модули, коллекции, JSON-хранилище, тесты;
- ПР3 — объектная модель: `User`, `Waypoint`, `Route`, `Review`;
- ПР5 — Django-проект, приложения `homepage`, `routes`, `reviews`,
  маршрутизация, страницы с данными и оформлением Bootstrap;
- ПР6 — шаблоны Django: базовый шаблон, наследование, include,
  контекст, циклы, условия, фильтры, именованные URL, собственные CSS,
  JavaScript и изображение.

- ПР7 — база данных SQLite: схема, импорт из JSON, 14 SQL-запросов,
  страницы подбора маршрута и статистики на данных из базы.

Веб-версия получает данные из SQLite обычными SQL-запросами; Django ORM
и формы создания данных ещё не используются.

На следующих этапах планируется:

- перенос сущностей в модели Django ORM и админ-зона;
- формы создания и редактирования маршрутов и отзывов;
- реализация пользователей;
- разработка REST API;
- контейнеризация приложения;
- настройка CI/CD.
