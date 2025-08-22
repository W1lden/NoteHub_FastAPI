from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqladmin import Admin

from notes.admin.auth import AdminAuth
from notes.admin.views import CategoryAdmin, NoteAdmin, UserAdmin
from notes.api.routers import main_router
from notes.core.config import settings
from notes.core.db import engine

from notes.web import main as web_main
from notes.web import auth as web_auth
from notes.web import notes as web_notes
from notes.web import chat as web_chat

app = FastAPI(title=settings.APP_TITLE, description=settings.DESCRIPTION)

app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET)
app.mount("/static", StaticFiles(directory="notes/static"), name="static")

app.include_router(main_router)
app.include_router(web_main.router)
app.include_router(web_auth.router)
app.include_router(web_notes.router)
app.include_router(web_chat.router)

auth_backend = AdminAuth(secret_key=f"{settings.ADMIN}")
admin = Admin(app=app, engine=engine, authentication_backend=auth_backend)

admin.add_view(UserAdmin)
admin.add_view(NoteAdmin)
admin.add_view(CategoryAdmin)
