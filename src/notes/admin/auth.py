from fastapi_users.password import PasswordHelper
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from starlette.requests import Request

from notes.core.db import AsyncSessionLocal
from notes.db.models.user import User


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]

        async with AsyncSessionLocal() as session:
            user = await session.scalar(
                select(User).where(User.email == email)
            )

        if not user or not user.is_admin:
            return False

        helper = PasswordHelper()
        if not helper.verify_and_update(password, user.hashed_password):
            return False

        request.session.update({"user": user.id})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request):
        user_id = request.session.get("user")
        if not user_id:
            return None
        async with AsyncSessionLocal() as session:
            return await session.get(User, user_id)
