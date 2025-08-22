from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notes.core.db import get_async_session
from notes.db.models.note import Note

router = APIRouter(prefix="", tags=["web-main"], include_in_schema=False)
templates = Jinja2Templates(directory="notes/templates")

@router.get("/", name="web_main:index", response_class=HTMLResponse)
async def index(request: Request, session: AsyncSession = Depends(get_async_session)):
    user_id = request.session.get("user_id")
    user_notes = []
    if user_id:
        rows = await session.execute(
            select(Note)
            .where(Note.user_id == user_id)
            .order_by(Note.id.desc())
            .limit(10)
        )
        user_notes = rows.scalars().all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "notes": user_notes},
    )
