from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notes.db.crud.base import CRUDBase
from notes.db.models import Category


class CRUDCategory(CRUDBase):
    async def create(self, obj_in, session: AsyncSession):
        result = await session.execute(
            select(Category).where(Category.name == obj_in.name)
        )
        existing = result.scalars().first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Категория с именем '{obj_in.name}' уже существует",
            )

        return await super().create(obj_in, session)


category_crud = CRUDCategory(Category)
