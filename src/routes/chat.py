from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import MessageCreate, MessageOut
from src.crud import create_message, get_study_room
from src.routes.auth import get_current_user
from src.models import User
from jose import jwt, JWTError
import logging

# Set up logging
logger = logging.getLogger("src.routes.chat")
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/api/chat", tags=["chat"])
SECRET_KEY = "your-secret-key"  # Same as in auth.py
ALGORITHM = "HS256"
connections = {}  # {room_id: [WebSocket]}

async def broadcast_message(room_id: int, message: dict):
    if 'created_at' in message:
        message['created_at'] = message['created_at'].isoformat()  # Convert datetime to string
    if room_id in connections:
        print(connections[room_id])
        for ws in connections[room_id]:
            await ws.send_json(message)

@router.websocket("/{room_id}")
async def chat_websocket(room_id: int, websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        logger.debug("No token found, closing WebSocket.")
        return

    try:
        # Decode the token and authenticate user
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = db.query(User).filter(User.username == username).first()
        if not user or not get_study_room(db, room_id):
            await websocket.close(code=1008)
            logger.debug(f"User {username} is not authorized or study room {room_id} does not exist. Closing WebSocket.")
            return
        logger.debug(f"Decoded token for user: {username}")
    except JWTError:
        await websocket.close(code=1008)
        logger.debug("Invalid JWT token. Closing WebSocket.")
        return

    # Add the WebSocket to the room connections
    if room_id not in connections:
        connections[room_id] = []
    connections[room_id].append(websocket)
    logger.debug(f"User {username} connected to room {room_id}. Current connections: {len(connections[room_id])}")

    try:
        # Listening for incoming messages
        while True:
            data = await websocket.receive_json()
            logger.debug(f"Received message: {data}")  # Log the incoming message

            # Ensure the message is correctly created
            try:
                message = MessageCreate(**data)
                logger.debug(f"Message created: {message}")
            except Exception as e:
                logger.error(f"Error creating message from received data: {e}")
                continue

            # Try saving the message to the database
            db_message = create_message(db, message.content, message.room_id, user)
            if db_message:
                logger.debug(f"Message saved to database with ID: {db_message.id}")
                message_out = MessageOut(
                    id=db_message.id,
                    content=db_message.content,
                    user_id=db_message.user_id,
                    room_id=db_message.room_id,
                    created_at=db_message.created_at,
                    username=user.username
                )
                # Broadcast to all users in the room
                await broadcast_message(room_id, message_out.dict())
            else:
                logger.warning(f"Failed to save message to database for room {room_id}.")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for room {room_id}. Cleaning up...")
        connections[room_id].remove(websocket)
        if not connections[room_id]:
            del connections[room_id]
        logger.debug(f"Room {room_id} has no more active connections.")

    except Exception as e:
        logger.error(f"Error in WebSocket communication: {e}")
        connections[room_id].remove(websocket)
        if not connections[room_id]:
            del connections[room_id]
        await websocket.close(code=1008)
