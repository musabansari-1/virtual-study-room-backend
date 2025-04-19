from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import Base, engine
from src.routes.auth import router as auth_router
from src.routes.study_rooms import router as study_room_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow React frontend to call APIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(auth_router)
app.include_router(study_room_router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Virtual Study Room API"}