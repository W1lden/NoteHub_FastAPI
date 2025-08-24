from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notes.core.db import get_async_session
from notes.db.models import User
from notes.db.crud.note import note_crud

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request, session: AsyncSession = Depends(get_async_session)):
    templates = request.app.state.templates
    user_id = request.session.get("user_id")
    if not user_id:
        return templates.TemplateResponse("index.html", {"request": request, "user": None})
    user = (await session.execute(select(User).where(User.id == user_id))).scalars().first()
    notes = await note_crud.get_multi_filtered(session=session, user=user)
    return templates.TemplateResponse("index.html", {"request": request, "user": user, "notes": notes})
