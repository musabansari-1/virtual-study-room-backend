from sqlalchemy.orm import Session
from src.models import User, StudyRoom
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, username: str, email: str, password: str):
    hashed_password = pwd_context.hash(password)
    db_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def create_study_room(db: Session, name: str, subject: str, user: User):
    db_room = StudyRoom(name=name, subject=subject)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    user.study_rooms.append(db_room)
    db.commit()
    return db_room

def get_study_rooms(db: Session):
    return db.query(StudyRoom).all()

def get_study_room(db: Session, room_id: int):
    return db.query(StudyRoom).filter(StudyRoom.id == room_id).first()

def join_study_room(db: Session, room_id: int, user: User):
    room = get_study_room(db, room_id)
    if not room:
        return None
    if user not in room.users:
        user.study_rooms.append(room)
        db.commit()
    return room