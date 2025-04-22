# Virtual Study Room
A collaborative platform for remote study sessions.

## Setup
1. Clone: `git clone <repo>`
2. Run: ` python -m venv venv; Linux: source venv/bin/activate; Windows: venv\Scripts\activate;  pip install -r requirements.txt; uvicorn src.main:app --reload`
4. Database: SQLite (`studyroom.db`).
5. Access: `http://localhost:8000`

## APIs
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/study-rooms`
- `POST /api/study-rooms`
- `POST /api/study-rooms/:id/join`

## Docs
- Swagger: `http://localhost:8000/docs`