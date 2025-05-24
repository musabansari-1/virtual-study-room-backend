import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.database import Base, engine
from src.routes.auth import router as auth_router
from src.routes.study_rooms import router as study_room_router
from src.routes.chat import router as chat_router
from src.routes.profile import router as profile_router
from src.routes.video import router as video_router

# Configure logging
logger = logging.getLogger()  # Root logger
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.debug("Logging initialized in main.py")

Base.metadata.create_all(bind=engine)
app = FastAPI()

# Log all incoming requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    auth_header = request.headers.get("authorization", "None")
    logger.debug(f"Incoming request: {request.method} {request.url.path} Authorization: {auth_header[:50]}...")
    response = await call_next(request)
    logger.debug(f"Response status: {response.status_code}")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(study_room_router)
app.include_router(chat_router)
app.include_router(profile_router)
app.include_router(video_router)


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Virtual Study Room API"}