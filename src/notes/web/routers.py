from fastapi import APIRouter

from notes.web import (auth_router, chat_router, chat_ws_router, main_router,
                       notes_router)

web_router = APIRouter()

web_router.include_router(main_router, tags=["main"])
web_router.include_router(auth_router, prefix="/auth", tags=["auth"])
web_router.include_router(chat_router, prefix="/chat", tags=["chat"])
web_router.include_router(chat_ws_router, tags=["chat-ws"])
web_router.include_router(notes_router, prefix="/notes", tags=["notes"])
