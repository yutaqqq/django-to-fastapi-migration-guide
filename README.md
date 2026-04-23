# django-to-fastapi-migration-guide

[![CI](https://github.com/yutaqqq/django-to-fastapi-migration-guide/actions/workflows/ci.yml/badge.svg)](https://github.com/yutaqqq/django-to-fastapi-migration-guide/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Практическое руководство по миграции с Django REST Framework на FastAPI.  
Один и тот же каталог товаров реализован на обоих фреймворках — можно сравнивать подход side-by-side.

## Структура

```
django_app/          # Django + DRF реализация
  catalog/
    models.py        # ORM-модели (Category, Product)
    serializers.py   # DRF сериализаторы
    views.py         # ViewSet
    tests.py         # тесты с APIClient
  myproject/
    settings.py
    urls.py

fastapi_app/         # FastAPI + SQLAlchemy (async) реализация
  routers/
    catalog.py       # роуты каталога
  models.py          # SQLAlchemy модели
  schemas.py         # Pydantic схемы
  database.py        # engine + get_db dependency
  main.py
  tests/
    conftest.py      # фикстуры (in-memory SQLite, AsyncClient)
    test_catalog.py

benchmarks/
  locustfile.py      # нагрузочные сценарии для обоих сервисов
```

## Ключевые различия

| Аспект | Django DRF | FastAPI |
|--------|-----------|---------|
| ORM | Django ORM (sync) | SQLAlchemy async |
| Сериализация | `Serializer` классы | Pydantic схемы |
| Роутинг | `urls.py` + `ViewSet` | `APIRouter` + декораторы |
| Тесты | `APIClient` (sync) | `AsyncClient` + `pytest-asyncio` |
| Документация | `/api/schema/` (опционально) | `/docs` (автоматически) |

## Запуск Django

```bash
cd django_app
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# тесты
python manage.py test catalog --verbosity=2
```

## Запуск FastAPI

```bash
cd fastapi_app
pip install -r requirements.txt

# запуск (DATABASE_URL по умолчанию: sqlite+aiosqlite:///./catalog.db)
DATABASE_URL=sqlite+aiosqlite:///./catalog.db uvicorn fastapi_app.main:app --reload

# тесты
pytest tests/ -v
```

Документация доступна на `http://localhost:8000/docs`.

## Переменные окружения (FastAPI)

| Переменная | По умолчанию | Описание |
|-----------|--------------|---------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./catalog.db` | URL базы данных (поддерживает PostgreSQL через `postgresql+asyncpg://`) |
