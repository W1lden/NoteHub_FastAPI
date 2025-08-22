from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notes.core.db import get_async_session
from notes.core.user import get_user_manager
from notes.api.schemas.user import UserCreate
from notes.db.models import User

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login-form")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_async_session),
    user_manager=Depends(get_user_manager),
):
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        templates = request.app.state.templates
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Неверный email или пароль"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    verified, updated_password_hash = user_manager.password_helper.verify_and_update(password, user.hashed_password)
    if not verified:
        templates = request.app.state.templates
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Неверный email или пароль"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if updated_password_hash:
        user.hashed_password = updated_password_hash
        await session.commit()
    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.post("/register-form")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    user_manager=Depends(get_user_manager),
):
    try:
        user = await user_manager.create(UserCreate(email=email, password=password))
    except Exception:
        templates = request.app.state.templates
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Не удалось зарегистрироваться"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
