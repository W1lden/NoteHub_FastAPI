import logging
from typing import List, Optional, TypeVar

from fastapi import HTTPException, status
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from notes.db.crud.base import CRUDBase
from notes.db.models import Category, Note, note_category_association

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Note)


class CRUDNote(CRUDBase[ModelType]):
    async def create_with_categories(
        self,
        obj_in: dict,
        category_ids: Optional[List[int]],
        session: AsyncSession,
    ) -> ModelType:
        note = self.model(**obj_in)
        session.add(note)
        await session.flush()

        if category_ids:
            existing_ids = await session.execute(
                select(Category.id).where(Category.id.in_(category_ids))
            )
            existing_ids = set(existing_ids.scalars().all())
            missing_ids = set(category_ids) - existing_ids
            if missing_ids:
                logger.warning(
                    f"Попытка создать заметку {note.id} с несуществующими категориями: {missing_ids}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Категории не найдены: {sorted(missing_ids)}",
                )

            stmt = insert(note_category_association).values(
                [
                    {"note_id": note.id, "category_id": cat_id}
                    for cat_id in category_ids
                ]
            )
            await session.execute(stmt)

        await session.commit()

        logger.info(
            f"Заметка {note.id} создана пользователем {note.user_id}, категории: {category_ids or []}"
        )

        note_with_categories = await session.execute(
            select(Note)
            .options(selectinload(Note.categories))
            .where(Note.id == note.id)
        )
        return note_with_categories.scalars().first()

    async def get_multi_filtered(
        self, session: AsyncSession, user
    ) -> List[ModelType]:
        stmt = select(self.model).options(selectinload(self.model.categories))
        if not user.is_admin:
            stmt = stmt.where(self.model.user_id == user.id)
        result = await session.execute(stmt)
        notes = result.scalars().all()
        logger.info(
            f"Пользователь {user.id} получил список заметок (кол-во: {len(notes)})"
        )
        return notes

    async def get_by_id_filtered(
        self, note_id: int, session: AsyncSession, user
    ) -> Optional[ModelType]:
        stmt = (
            select(self.model)
            .where(self.model.id == note_id)
            .options(selectinload(self.model.categories))
        )
        if not user.is_admin:
            stmt = stmt.where(self.model.user_id == user.id)
        result = await session.execute(stmt)
        note = result.scalars().first()
        if note:
            logger.info(f"Заметка {note.id} получена пользователем {user.id}")
        else:
            logger.warning(
                f"Заметка {note_id} не найдена или доступ запрещён (пользователь {user.id})"
            )
        return note

    async def update_with_categories(
        self, db_obj: ModelType, obj_in: dict, session: AsyncSession
    ) -> ModelType:
        for field, value in obj_in.items():
            if field != "category_ids" and value is not None:
                setattr(db_obj, field, value)

        if "category_ids" in obj_in and obj_in["category_ids"] is not None:
            await session.execute(
                delete(note_category_association).where(
                    note_category_association.c.note_id == db_obj.id
                )
            )

            if obj_in["category_ids"]:
                existing_ids = await session.execute(
                    select(Category.id).where(
                        Category.id.in_(obj_in["category_ids"])
                    )
                )
                existing_ids = set(existing_ids.scalars().all())

                missing_ids = set(obj_in["category_ids"]) - existing_ids
                if missing_ids:
                    logger.warning(
                        f"Попытка обновить заметку {db_obj.id} с несуществующими категориями: {missing_ids}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Категории не найдены: {sorted(missing_ids)}",
                    )

                stmt = insert(note_category_association).values(
                    [
                        {"note_id": db_obj.id, "category_id": cat_id}
                        for cat_id in obj_in["category_ids"]
                    ]
                )
                await session.execute(stmt)

        await session.commit()

        logger.info(f"Заметка {db_obj.id} обновлена. Новые данные: {obj_in}")

        note_with_categories = await session.execute(
            select(Note)
            .options(selectinload(Note.categories))
            .where(Note.id == db_obj.id)
        )
        return note_with_categories.scalars().first()


note_crud = CRUDNote(Note)
