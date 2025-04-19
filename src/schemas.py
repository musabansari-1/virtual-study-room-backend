from pydantic import BaseModel, EmailStr, constr
from datetime import datetime

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9]+$')
    email: EmailStr
    password: constr(min_length=8)

class UserOut(BaseModel):
    username: str
    email: EmailStr
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class StudyRoomCreate(BaseModel):
    name: str
    subject: str

class StudyRoomOut(BaseModel):
    id: int
    name: str
    subject: str
    created_at: datetime
    class Config:
        from_attributes = True