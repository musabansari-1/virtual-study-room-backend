from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import StudyRoomCreate, StudyRoomOut
from src.crud import create_study_room, get_study_rooms, join_study_room
from src.routes.auth import get_current_user
from src.models import User

router = APIRouter(prefix="/api/study-rooms", tags=["study-rooms"])

@router.get("/", response_model=list[StudyRoomOut])
async def list_study_rooms(db: Session = Depends(get_db)):
    return get_study_rooms(db)

@router.post("/", response_model=StudyRoomOut)
async def create_study_room(room: StudyRoomCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return create_study_room(db, room.name, room.subject, user)

@router.post("/{room_id}/join", response_model=StudyRoomOut)
async def join_study_room(room_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    room = join_study_room(db, room_id, user)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room