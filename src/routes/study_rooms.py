from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import StudyRoomCreate, StudyRoomOut
from src.crud import create_study_room, get_study_rooms, join_study_room, delete_study_room
from src.routes.auth import get_current_user
from src.models import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/study-rooms", tags=["study_rooms"])

@router.post("/", response_model=StudyRoomOut)
async def create_room(room: StudyRoomCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.debug(f"Creating room: {room.dict()} for user: {current_user.username}")
    return create_study_room(db, room.name, room.subject, current_user)

@router.get("/", response_model=list[StudyRoomOut])
async def list_rooms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.debug(f"Listing rooms for user: {current_user.username}")
    return get_study_rooms(db)

@router.post("/{room_id}/join/", response_model=StudyRoomOut)
async def join_room(room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.debug(f"User {current_user.username} joining room {room_id}")
    room = join_study_room(db, room_id, current_user)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.delete("/{room_id}", response_model=dict)
async def delete_room(room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.debug(f"User {current_user.username} deleting room {room_id}")
    success = delete_study_room(db, room_id, current_user)
    if not success:
        raise HTTPException(status_code=403, detail="Not authorized to delete this room")
    return {"message": "Room deleted"}