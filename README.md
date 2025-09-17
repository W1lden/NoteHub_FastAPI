# 📝 NoteHub - проект удобных заметок

Этот проект позволяет создавать, писать, и удалять заметки. Так же есть возможность задавать им категории, чтобы фильтровать их, тем самым повысить вашу продуктивность и организованность!

---

## 🧱 Стек технологий

- Python
- FastAPI
- Alembic
- SQLAlchemy
- PostgreSQL
- Jinja2
- WebSocket
- Redis
- Docker + Docker Compose
- HTML + CSS + JavaScript

---

## 🗂 Структура проекта

```
solva-notes-fastapi-final-W1lden/
├─ src/
│  ├─ migrations/
│  │  ├─ versions/
│  │  │  ├─ 6906504e637d_add_category_model.py
│  │  │  ├─ 81667a168fa3_add_relationship_between_user_and_note.py
│  │  │  └─ 98967379f929_add_is_admin_to_user.py
│  │  ├─ env.py
│  │  ├─ README
│  │  └─ script.py.mako
│  ├─ notes/
│  │  ├─ admin/
│  │  │  ├─ __init__.py
│  │  │  ├─ auth.py
│  │  │  └─ views.py
│  │  ├─ api/
│  │  │  ├─ endpoints/
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ category.py
│  │  │  │  ├─ note.py
│  │  │  │  └─ user.py
│  │  │  ├─ schemas/
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ category.py
│  │  │  │  ├─ common.py
│  │  │  │  ├─ note.py
│  │  │  │  └─ user.py
│  │  │  ├─ __init__.py
│  │  │  ├─ routers.py
│  │  │  └─ validators.py
│  │  ├─ core/
│  │  │  ├─ __init__.py
│  │  │  ├─ base.py
│  │  │  ├─ config.py
│  │  │  ├─ constants.py
│  │  │  ├─ db.py
│  │  │  ├─ redis.py
│  │  │  └─ user.py
│  │  ├─ db/
│  │  │  ├─ crud/
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ base.py
│  │  │  │  ├─ category.py
│  │  │  │  └─ note.py
│  │  │  ├─ models/
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ category.py
│  │  │  │  ├─ note.py
│  │  │  │  └─ user.py
│  │  │  └─ __init__.py
│  │  ├─ static/
│  │  │  ├─ css/
│  │  │  │  └─ style.css
│  │  │  ├─ img/
│  │  │  │  └─ logo.png
│  │  │  └─ js/
│  │  │     └─ chat.js
│  │  ├─ templates/
│  │  │  ├─ auth/
│  │  │  │  ├─ login.html
│  │  │  │  └─ register.html
│  │  │  ├─ chat/
│  │  │  │  └─ chat.html
│  │  │  ├─ notes/
│  │  │  │  ├─ create.html
│  │  │  │  ├─ detail.html
│  │  │  │  ├─ edit.html
│  │  │  │  └─ list.html
│  │  │  ├─ base.html
│  │  │  └─ index.html
│  │  ├─ web/
│  │  │  ├─ __init__.py
│  │  │  ├─ auth.py
│  │  │  ├─ chat.py
│  │  │  ├─ main.py
│  │  │  ├─ notes.py
│  │  │  └─ routers.py
│  │  ├─ __init__.py
│  │  └─ main.py
│  ├─ .env
│  ├─ alembic.ini
│  ├─ Dockerfile
│  └─ requirements.txt
├─ .gitignore
├─ docker-compose.yml
└─ README.md
```

---

## 🚀 Запуск проекта

1. Клонируйте репозиторий:
```bash
git clone https://github.com/W1lden/NoteHub_FastAPI.git
```

2. Создайте .env файл в каталоге src. Вот пример:
```env_example
PRODUCTION=False
APP_TITLE=NoteHub
DESCRIPTION=NoteHub - проект удобных заметок
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/postgres
SECRET_WORD=t1k5m2uu
SECRET_KEY=t1k5m2uu
ADMIN=SUPERSECRET
REDIS_URL=redis://redis:6379/0
```

3. Соберите и запустите Docker контейнер:
```bash 
docker compose up --build -d
```

4. В браузере прейдите на сайт веб-приложения:
```bash
http://0.0.0.0:8000/
```

5. Также можете перейти на страницу документации:веб-приложения:
```bash
http://0.0.0.0:8000/docs
```

---

## 🛠️ Запуск админки

1. Создайте админ-пользователя в ручке /auth/register/, например:
```bash
{
  "email": "user@example.com",
  "password": "string",
  "is_active": true,
  "is_superuser": true,
  "is_verified": true,
  "is_admin": true
}
```

2. Зайдите в админ панель:
```bash
http://0.0.0.0:8000/admin/
```
---
## 🌐 Страницы
- http://0.0.0.0:8000/auth/register - регистрация пользователя;
- http://0.0.0.0:8000/auth/login - аутентификация пользователя;
- http://0.0.0.0:8000/notes - заметки пользователя;
- http://0.0.0.0:8000/notes/new - созать заметку;
- http://0.0.0.0:8000/chat/ - чат.
---

## 🌐 Ручки
- POST /auth/register/ - регистрация пользователя, после создания нужно авторизоваться с помощью кнопки Authorize в правом верхнем углу документации;
- POST /category/ - создать категорию;
- GET /category/all - посмотреть все свои категории;
- GET /category/{id} - посмотреть категорию по id;
- PATCH /category/{id}/update - обновить категорию по id;
- DELETE /category/{id} - удалить категорию по id;
- POST /note/ - создать категорию;
- GET /note/all - посмотреть все свои заметки;
- GET /note/{id} - посмотреть заметку по id;
- PATCH /note/{id}/update - обновить заметку по id;
- DELETE /note/{id} - удалить заметку по id;
---

## 👤 Автор

[W1lden (GitHub)](https://github.com/W1lden)
