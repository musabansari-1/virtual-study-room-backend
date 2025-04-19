# Import SQLAlchemy tools
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database file
SQLALCHEMY_DATABASE_URL = "sqlite:///./studyroom.db"
# Connect to database
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# Create sessions for queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base for models
Base = declarative_base()

# Dependency to provide database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()