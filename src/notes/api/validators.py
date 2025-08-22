from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from notes.db.crud.category import category_crud
from notes.db.crud.note import note_crud


async def check_note_exist(note_id: int, session: AsyncSession, user):
    note = await note_crud.get(note_id, session)
    if note is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Заметка не найдена!"
        )

    if (not user.is_admin) and (note.user_id != user.id):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Нет доступа к этой заметке",
        )

    return note


async def check_category_exist(category_id: int, session: AsyncSession):
    category = await category_crud.get(category_id, session)
    if category is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Категория не найдена!"
        )
    return category
