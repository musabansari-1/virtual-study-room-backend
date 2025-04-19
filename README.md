# Virtual Study Room
A collaborative platform for remote study sessions.

## Setup
1. Clone: `git clone <repo>`
2. Backend: `cd virtual-study-room; python -m venv venv; source venv/bin/activate; pip install -r requirements.txt; uvicorn src.main:app --reload`
3. Frontend: `cd frontend; npm install; npm start`
4. Database: SQLite (`studyroom.db`).
5. Access: `http://localhost:3000`

## APIs
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/study-rooms`
- `POST /api/study-rooms`
- `POST /api/study-rooms/:id/join`

## Docs
- Swagger: `http://localhost:8000/docs`