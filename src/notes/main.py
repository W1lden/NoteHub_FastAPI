from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from sqladmin import Admin

from notes.admin.auth import AdminAuth
from notes.admin.views import CategoryAdmin, NoteAdmin, UserAdmin
from notes.api.routers import api_router
from notes.core.config import settings
from notes.core.db import engine
from notes.web.routers import web_router

app = FastAPI(title=settings.APP_TITLE, description=settings.DESCRIPTION)

app.add_middleware(
    SessionMiddleware,
    secret_key=str(getattr(settings, "SESSION_SECRET", settings.SECRET_KEY)),
    session_cookie="notes_session",
    same_site="lax",
)

templates = Jinja2Templates(directory="notes/templates")
app.state.templates = templates

app.mount("/static", StaticFiles(directory="notes/static"), name="static")

app.include_router(api_router)
app.include_router(web_router, include_in_schema=False)

auth_backend = AdminAuth(secret_key=f"{settings.ADMIN}")
admin = Admin(app=app, engine=engine, authentication_backend=auth_backend)
admin.add_view(UserAdmin)
admin.add_view(NoteAdmin)
admin.add_view(CategoryAdmin)
