import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notes.core.constants import (HISTORY_LAST_N_MESSAGES,
                                  HISTORY_MAX_SAVE_LEN, LIST_END,
                                  REDIS_CHAT_HISTORY_KEY)
from notes.core.db import get_async_session
from notes.core.redis import get_redis
from notes.db.models import User

router = APIRouter()
ws_router = APIRouter()
connections = set()


@router.get("/", response_class=HTMLResponse)
async def chat_page(
    request: Request, session: AsyncSession = Depends(get_async_session)
):
    templates = request.app.state.templates
    user_id = request.session.get("user_id")
    user = None
    if user_id:
        user = (
            (await session.execute(select(User).where(User.id == user_id)))
            .scalars()
            .first()
        )
    return templates.TemplateResponse(
        "chat/chat.html", {"request": request, "user": user}
    )


@ws_router.websocket("/ws/anon-chat")
async def anon_chat_ws(websocket: WebSocket):
    await websocket.accept()
    nickname = websocket.query_params.get("nickname")
    if not nickname:
        await websocket.close()
        return
    connections.add(websocket)
    r = await get_redis()
    try:
        history = await r.lrange(
            REDIS_CHAT_HISTORY_KEY, HISTORY_LAST_N_MESSAGES, LIST_END
        )
        for item in history:
            await websocket.send_text(item)
        join_event = {
            "type": "system",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nickname": "",
            "text": f"{nickname} вошёл в чат",
        }
        await r.rpush(
            REDIS_CHAT_HISTORY_KEY, json.dumps(join_event, ensure_ascii=False)
        )
        await r.ltrim(REDIS_CHAT_HISTORY_KEY, HISTORY_MAX_SAVE_LEN, LIST_END)
        for conn in list(connections):
            await conn.send_text(json.dumps(join_event, ensure_ascii=False))
        while True:
            text = await websocket.receive_text()
            msg = {
                "type": "message",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "nickname": nickname,
                "text": text.strip(),
            }
            if not msg["text"]:
                continue
            await r.rpush(
                REDIS_CHAT_HISTORY_KEY, json.dumps(msg, ensure_ascii=False)
            )
            await r.ltrim(
                REDIS_CHAT_HISTORY_KEY, HISTORY_MAX_SAVE_LEN, LIST_END
            )
            for conn in list(connections):
                await conn.send_text(json.dumps(msg, ensure_ascii=False))
    except WebSocketDisconnect:
        leave_event = {
            "type": "system",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nickname": "",
            "text": f"{nickname} вышел из чата",
        }
        await r.rpush(
            REDIS_CHAT_HISTORY_KEY, json.dumps(leave_event, ensure_ascii=False)
        )
        await r.ltrim(REDIS_CHAT_HISTORY_KEY, HISTORY_MAX_SAVE_LEN, LIST_END)
        connections.discard(websocket)
        for conn in list(connections):
            await conn.send_text(json.dumps(leave_event, ensure_ascii=False))
