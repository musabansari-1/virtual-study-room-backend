from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import UserProfile
from src.routes.auth import get_current_user
from src.models import User

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user