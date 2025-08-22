from typing import Optional

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.hash import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notes.core.db import get_async_session
from notes.db.models.user import User

router = APIRouter(prefix="", tags=["web-auth"], include_in_schema=False)
templates = Jinja2Templates(directory="notes/templates")


def _redirect(url: str, *, see_other: bool = True) -> RedirectResponse:
    return RedirectResponse(
        url=url,
        status_code=status.HTTP_303_SEE_OTHER if see_other else status.HTTP_302_FOUND,
    )


async def _get_user_by_email(email: str, session: AsyncSession) -> Optional[User]:
    res = await session.execute(select(User).where(User.email == email))
    return res.scalars().first()


@router.get("/register", name="web_auth:register", response_class=HTMLResponse)
async def register_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request, "error": None, "values": {"email": ""}},
    )


@router.post("/register", name="web_auth:register_post")
async def register_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_async_session),
):
    email = email.strip().lower()

    # уникальность email
    existing = await _get_user_by_email(email, session)
    if existing:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "Пользователь с таким email уже существует.",
                "values": {"email": email},
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if len(password) <= 8:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "Пароль должен быть длиннее 8 символов.",
                "values": {"email": email},
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if email in password:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "Пароль не должен содержать ваш email.",
                "values": {"email": email},
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user = User(email=email, hashed_password=bcrypt.hash(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # авто-авторизация
    request.session["user_id"] = user.id
    request.session["email"] = user.email

    return _redirect("/")


@router.get("/login", name="web_auth:login", response_class=HTMLResponse)
async def login_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "error": None, "values": {"email": ""}},
    )


@router.post("/login", name="web_auth:login_post")
async def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_async_session),
):
    email = email.strip().lower()
    user = await _get_user_by_email(email, session)

    if not user or not bcrypt.verify(password, user.hashed_password):
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Неверный email или пароль.",
                "values": {"email": email},
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # авторизация
    request.session["user_id"] = user.id
    request.session["email"] = user.email

    return _redirect("/")


@router.post("/logout", name="web_auth:logout")
async def logout(request: Request):
    request.session.clear()
    return _redirect("/")
