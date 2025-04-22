from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import User
from src.crud import authenticate_user, create_user, get_user_by_username
from src.schemas import UserCreate, UserOut, Token, LoginCredentials
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])
SECRET_KEY = "your-secret-key"  # Ensure consistency
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    logger.debug(f"Received token: {token[:10] if token else 'None'}... (length: {len(token) if token else 0})")
    if not token:
        logger.error("No token provided in Authorization header")
        raise HTTPException(status_code=401, detail="No token provided")
    try:
        logger.debug("Attempting to decode JWT")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Token payload: {payload}")
        username: str = payload.get("sub")
        if username is None:
            logger.error("Token missing 'sub' claim")
            raise HTTPException(status_code=401, detail="Invalid authentication credentials: Missing 'sub' claim")
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            logger.error(f"Token expired for user: {username}, exp: {exp}")
            raise HTTPException(status_code=401, detail="Invalid authentication credentials: Token expired")
    except JWTError as e:
        logger.error(f"JWT validation failed: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid authentication credentials: {str(e)}")
    logger.debug(f"Looking up user: {username}")
    user = get_user_by_username(db, username)
    if user is None:
        logger.error(f"User not found: {username}")
        raise HTTPException(status_code=401, detail=f"User not found: {username}")
    logger.debug(f"User authenticated: {username}")
    return user

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    logger.debug(f"Registering user: {user.username}")
    db_user = create_user(db, user.username, user.email, user.password)
    return db_user

@router.post("/login", response_model=Token)
async def login(credentials: LoginCredentials, db: Session = Depends(get_db)):
    logger.debug(f"Login attempt for user: {credentials.username}")
    db_user = authenticate_user(db, credentials.username, credentials.password)
    if not db_user:
        logger.error(f"Login failed for user: {credentials.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=30)
    access_token = jwt.encode(
        {"sub": credentials.username, "exp": datetime.utcnow() + access_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    logger.debug(f"Login successful for user: {credentials.username}, token: {access_token[:10]}...")
    return {"access_token": access_token, "token_type": "bearer"}