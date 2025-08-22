from typing import Optional, List

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notes.core.db import get_async_session
from notes.db.models import Note, User, Category
from notes.db.crud.note import note_crud

router = APIRouter()

async def get_current_user(request: Request, session: AsyncSession) -> Optional[User]:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

@router.get("/", response_class=HTMLResponse)
async def notes_list(request: Request, session: AsyncSession = Depends(get_async_session)):
    templates = request.app.state.templates
    user = await get_current_user(request, session)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    notes = await note_crud.get_multi_filtered(session=session, user=user)
    return templates.TemplateResponse("notes/list.html", {"request": request, "notes": notes})

@router.get("/new", response_class=HTMLResponse)
async def notes_create_form(request: Request, session: AsyncSession = Depends(get_async_session)):
    templates = request.app.state.templates
    user = await get_current_user(request, session)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    categories = (await session.execute(select(Category))).scalars().all()
    return templates.TemplateResponse("notes/create.html", {"request": request, "categories": categories})

@router.post("")
async def notes_create(
    request: Request,
    title: str = Form(...),
    text: str = Form(""),
    category_ids: Optional[List[int]] = Form(None),
    session: AsyncSession = Depends(get_async_session),
):
    user = await get_current_user(request, session)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    obj_in = {"title": title, "text": text, "user_id": user.id}
    note = await note_crud.create_with_categories(obj_in=obj_in, category_ids=category_ids, session=session)
    return RedirectResponse(url=f"/notes/{note.id}", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/{note_id}", response_class=HTMLResponse)
async def notes_detail(note_id: int, request: Request, session: AsyncSession = Depends(get_async_session)):
    templates = request.app.state.templates
    user = await get_current_user(request, session)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    note = await note_crud.get_by_id_filtered(note_id=note_id, session=session, user=user)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    is_owner = note.user_id == user.id
    return templates.TemplateResponse("notes/detail.html", {"request": request, "note": note, "is_owner": is_owner})

@router.get("/{note_id}/edit", response_class=HTMLResponse)
async def notes_edit_form(note_id: int, request: Request, session: AsyncSession = Depends(get_async_session)):
    templates = request.app.state.templates
    user = await get_current_user(request, session)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    note = await note_crud.get_by_id_filtered(note_id=note_id, session=session, user=user)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    categories = (await session.execute(select(Category))).scalars().all()
    selected_ids = [c.id for c in note.categories]
    return templates.TemplateResponse("notes/edit.html", {"request": request, "note": note, "categories": categories, "selected_ids": selected_ids})

@router.post("/{note_id}/edit")
async def notes_edit(
    note_id: int,
    request: Request,
    title: str = Form(...),
    text: str = Form(""),
    category_ids: Optional[List[int]] = Form(None),
    session: AsyncSession = Depends(get_async_session),
):
    user = await get_current_user(request, session)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    note = await note_crud.get_by_id_filtered(note_id=note_id, session=session, user=user)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    update_data = {"title": title, "text": text, "category_ids": category_ids}
    await note_crud.update_with_categories(db_obj=note, obj_in=update_data, session=session)
    return RedirectResponse(url=f"/notes/{note_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/{note_id}/delete")
async def notes_delete(note_id: int, request: Request, session: AsyncSession = Depends(get_async_session)):
    user = await get_current_user(request, session)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    note = await note_crud.get_by_id_filtered(note_id=note_id, session=session, user=user)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await note_crud.delete(db_obj=note, session=session)
    return RedirectResponse(url="/notes", status_code=status.HTTP_303_SEE_OTHER)
