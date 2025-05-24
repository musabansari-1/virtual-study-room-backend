import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database import Base, get_db
from src.models import User, StudyRoom, Message
import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def create_test_user():
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "secure123"}
    )
    return response.json()

def login_test_user():
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "secure123"}
    )
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_register_user():
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "secure123"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

@pytest.mark.asyncio
async def test_login_user():
    create_test_user()
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "secure123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_create_room():
    create_test_user()
    token = login_test_user()
    response = client.post(
        "/api/study-rooms",
        json={"name": "Math Study", "subject": "Mathematics"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Math Study"

@pytest.mark.asyncio
async def test_delete_room():
    create_test_user()
    token = login_test_user()
    room_response = client.post(
        "/api/study-rooms",
        json={"name": "Math Study", "subject": "Mathematics"},
        headers={"Authorization": f"Bearer {token}"}
    )
    room_id = room_response.json()["id"]
    response = client.delete(
        f"/api/study-rooms/{room_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Room deleted"

@pytest.mark.asyncio
async def test_join_room():
    create_test_user()
    token = login_test_user()
    room_response = client.post(
        "/api/study-rooms",
        json={"name": "Math Study", "subject": "Mathematics"},
        headers={"Authorization": f"Bearer {token}"}
    )
    room_id = room_response.json()["id"]
    response = client.post(
        f"/api/study-rooms/{room_id}/join",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == room_id

@pytest.mark.asyncio
async def test_chat_messages():
    create_test_user()
    token = login_test_user()
    room_response = client.post(
        "/api/study-rooms",
        json={"name": "Math Study", "subject": "Mathematics"},
        headers={"Authorization": f"Bearer {token}"}
    )
    room_id = room_response.json()["id"]
    # Simulate message creation (since WebSocket is harder to test)
    db = TestingSessionLocal()
    db.add(Message(content="Hello", room_id=room_id, user_id=1, timestamp=datetime.datetime.utcnow()))
    db.commit()
    response = client.get(
        f"/api/chat/{room_id}/messages",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) > 0