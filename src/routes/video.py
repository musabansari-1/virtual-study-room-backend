from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from src.routes.auth import get_current_user
from src.models import User
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/video", tags=["video"])

# Store WebSocket connections by room_id
video_connections = {}

@router.websocket("/{room_id}")
async def video_websocket(room_id: int, websocket: WebSocket, user: User = Depends(get_current_user)):
    await websocket.accept()
    if room_id not in video_connections:
        video_connections[room_id] = []
    video_connections[room_id].append({"websocket": websocket, "username": user.username})
    logger.debug(f"User {user.username} connected to video room {room_id}")

    try:
        # Broadcast user joined
        await broadcast(room_id, {
            "type": "user_joined",
            "username": user.username
        }, exclude=websocket)

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            logger.debug(f"Video message in room {room_id}: {message}")

            # Handle WebRTC signaling messages
            if message["type"] in ["offer", "answer", "ice-candidate"]:
                target_username = message.get("target")
                if target_username:
                    # Send to specific user
                    for conn in video_connections[room_id]:
                        if conn["username"] == target_username:
                            await conn["websocket"].send_text(json.dumps({
                                "type": message["type"],
                                "sender": user.username,
                                "data": message["data"]
                            }))
                            break
            else:
                # Broadcast other messages (e.g., mute, video off)
                await broadcast(room_id, message, exclude=websocket)

    except WebSocketDisconnect:
        video_connections[room_id] = [
            conn for conn in video_connections[room_id] if conn["websocket"] != websocket
        ]
        logger.debug(f"User {user.username} disconnected from video room {room_id}")
        await broadcast(room_id, {
            "type": "user_left",
            "username": user.username
        })

async def broadcast(room_id: int, message: dict, exclude: WebSocket = None):
    for conn in video_connections.get(room_id, []):
        if conn["websocket"] != exclude:
            await conn["websocket"].send_text(json.dumps(message))