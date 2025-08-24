import json
from datetime import datetime, timezone

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from notes.core.redis import get_redis

router = APIRouter()
ws_router = APIRouter()
connections = set()


@router.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse("chat/chat.html", {"request": request})


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
        history = await r.lrange("chat:history", -20, -1)
        for item in history:
            await websocket.send_text(item)
        join_event = {
            "type": "system",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nickname": "",
            "text": f"{nickname} вошёл в чат",
        }
        await r.rpush(
            "chat:history", json.dumps(join_event, ensure_ascii=False)
        )
        await r.ltrim("chat:history", -1000, -1)
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
            await r.rpush("chat:history", json.dumps(msg, ensure_ascii=False))
            await r.ltrim("chat:history", -1000, -1)
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
            "chat:history", json.dumps(leave_event, ensure_ascii=False)
        )
        await r.ltrim("chat:history", -1000, -1)
        connections.discard(websocket)
        for conn in list(connections):
            await conn.send_text(json.dumps(leave_event, ensure_ascii=False))
