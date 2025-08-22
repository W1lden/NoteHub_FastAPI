from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="", tags=["web-chat"], include_in_schema=False)
templates = Jinja2Templates(directory="notes/templates")

@router.get("/chat", name="web_chat:chat", response_class=HTMLResponse)
async def chat(request: Request):
    return templates.TemplateResponse("chat/chat.html", {"request": request})
