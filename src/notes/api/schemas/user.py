from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    is_admin: bool


class UserCreate(schemas.BaseUserCreate):
    is_admin: bool = False


class UserUpdate(schemas.BaseUserUpdate):
    is_admin: Optional[bool]
