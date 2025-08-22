from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="", tags=["web-notes"], include_in_schema=False)
templates = Jinja2Templates(directory="notes/templates")

@router.get("/notes", name="web_notes:list_notes", response_class=HTMLResponse)
async def list_notes(request: Request):
    return templates.TemplateResponse("notes/list.html", {"request": request})

@router.get("/notes/new", name="web_notes:create_note", response_class=HTMLResponse)
async def create_note(request: Request):
    return templates.TemplateResponse("notes/create.html", {"request": request})
