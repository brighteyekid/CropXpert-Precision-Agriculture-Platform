"""WebSocket router — live sensor data push."""
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from core.security import decode_access_token
from core.mqtt_client import ws_clients

logger = logging.getLogger("cropxpert.ws")
router = APIRouter()

# Active connections with farmer_id mapping
_connections: dict[int, set[WebSocket]] = {}


def broadcast_to_farmer(farmer_id: int, message: dict):
    """Push a message to all WebSocket connections for a given farmer."""
    sockets = _connections.get(farmer_id, set())
    dead = set()
    for ws in sockets:
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(ws.send_json(message))
            else:
                loop.run_until_complete(ws.send_json(message))
        except Exception:
            dead.add(ws)
    _connections[farmer_id] -= dead


@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    # Validate JWT
    try:
        payload = decode_access_token(token)
        farmer_id = payload.get("farmer_id")
    except Exception:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await websocket.accept()
    logger.info("WebSocket connected for farmer %s", farmer_id)

    # Register connection
    if farmer_id not in _connections:
        _connections[farmer_id] = set()
    _connections[farmer_id].add(websocket)

    try:
        while True:
            # Keep connection alive — client can send pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for farmer %s", farmer_id)
    finally:
        _connections.get(farmer_id, set()).discard(websocket)
