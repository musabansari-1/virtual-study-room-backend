from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9]+$')
    email: EmailStr
    password: constr(min_length=8)

class UserOut(BaseModel):
    username: str
    email: EmailStr
    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    username: str
    email: EmailStr
    study_hours: float
    tasks_completed: int
    study_streak: int
    points: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class StudyRoomCreate(BaseModel):
    name: constr(min_length=3, max_length=50)
    subject: constr(min_length=3, max_length=50)

class StudyRoomOut(BaseModel):
    id: int
    name: str
    subject: str
    created_at: datetime
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: constr(min_length=1, max_length=500)
    room_id: int

class MessageOut(BaseModel):
    id: int
    content: str
    user_id: int
    room_id: int
    created_at: datetime
    username: str
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()  # Convert datetime to ISO format string
        }
        
        
class LoginCredentials(BaseModel):
    username: str
    password: str
        
    