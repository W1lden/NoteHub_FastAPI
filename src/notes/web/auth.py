from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users import InvalidPasswordException
from fastapi_users.exceptions import UserAlreadyExists

from notes.core.db import get_async_session
from notes.core.user import get_user_manager
from notes.api.schemas.user import UserCreate
from notes.db.models import User

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request, session: AsyncSession = Depends(get_async_session)):
    templates = request.app.state.templates
    user_id = request.session.get("user_id")
    user = None
    if user_id:
        user = (await session.execute(select(User).where(User.id == user_id))).scalars().first()
    return templates.TemplateResponse("auth/login.html", {"request": request, "user": user})

@router.post("/login-form")
async def login(
    request: Request,
    email: str = Form(""),
    password: str = Form(""),
    session: AsyncSession = Depends(get_async_session),
    user_manager=Depends(get_user_manager),
):
    templates = request.app.state.templates
    email = email.strip().lower()
    if not email or not password:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "user": None, "error": "Заполните email и пароль", "email_value": email},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "user": None, "error": "Неверный email или пароль", "email_value": email},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    verified, updated_password_hash = user_manager.password_helper.verify_and_update(password, user.hashed_password)
    if not verified:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "user": None, "error": "Неверный email или пароль", "email_value": email},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if updated_password_hash:
        user.hashed_password = updated_password_hash
        await session.commit()
    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request, session: AsyncSession = Depends(get_async_session)):
    templates = request.app.state.templates
    user_id = request.session.get("user_id")
    user = None
    if user_id:
        user = (await session.execute(select(User).where(User.id == user_id))).scalars().first()
    return templates.TemplateResponse("auth/register.html", {"request": request, "user": user})

@router.post("/register-form")
async def register(
    request: Request,
    email: str = Form(""),
    password: str = Form(""),
    user_manager=Depends(get_user_manager),
):
    templates = request.app.state.templates
    email = email.strip().lower()
    if not email or not password:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "user": None, "error": "Заполните email и пароль", "email_value": email},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if "@" not in email or "." not in email.split("@")[-1]:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "user": None, "error": "Некорректный email", "email_value": email},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    try:
        user = await user_manager.create(UserCreate(email=email, password=password))
    except UserAlreadyExists:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "user": None, "error": "Пользователь с таким email уже существует", "email_value": email},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except InvalidPasswordException as e:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "user": None, "error": e.reason or "Пароль не подходит требованиям", "email_value": email},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "user": None, "error": "Не удалось зарегистрироваться", "email_value": email},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
