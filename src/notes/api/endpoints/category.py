from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from notes.api.schemas.category import (CategoryCreate, CategoryDB,
                                        CategoryUpdate)
from notes.api.schemas.common import ID
from notes.api.validators import check_category_exist
from notes.core.db import get_async_session
from notes.core.user import current_user, is_admin
from notes.db.crud.category import category_crud

router = APIRouter()


# POST
@router.post(
    "/",
    response_model=CategoryDB,
    dependencies=[Depends(is_admin)],
    status_code=status.HTTP_201_CREATED,
)
async def create_new_category(
    new_category: CategoryCreate,
    session: AsyncSession = Depends(get_async_session),
):
    return await category_crud.create(new_category, session)


# GET
@router.get("/", response_model=list[CategoryDB])
async def get_all_categories(
    session: AsyncSession = Depends(get_async_session),
):
    return await category_crud.get_multi(session=session)


@router.get("/{category_id}", response_model=CategoryDB)
async def get_category_by_id(
    category_id: ID,
    session: AsyncSession = Depends(get_async_session),
):
    return await check_category_exist(category_id=category_id, session=session)


# PATCH
@router.patch("/{category_id}/update", response_model=CategoryDB)
async def update_category(
    category_id: ID,
    obj_in: CategoryUpdate,
    session: AsyncSession = Depends(get_async_session),
    admin=Depends(is_admin),
):
    category = await check_category_exist(category_id, session)
    return await category_crud.update(
        db_obj=category, obj_in=obj_in, session=session
    )


# DELETE
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: ID,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_user),
):
    category = await check_category_exist(
        category_id=category_id, session=session
    )
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нужны права администратора",
        )

    await category_crud.delete(category, session)
    return
