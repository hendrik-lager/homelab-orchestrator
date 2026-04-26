from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json

router = APIRouter()
_connections: list[WebSocket] = []

async def broadcast(message: dict):
    data = json.dumps(message)
    dead = []
    for ws in _connections:
        try:
            await ws.send_text(data)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _connections.remove(ws)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    _connections.append(websocket)
    try:
        while True:
            await asyncio.sleep(30)
            await websocket.send_text(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        if websocket in _connections:
            _connections.remove(websocket)
