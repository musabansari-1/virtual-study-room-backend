# Import SQLAlchemy types
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base

# Many-to-many table
user_study_room = Table(
    'user_study_room',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('study_room_id', Integer, ForeignKey('study_rooms.id'))
)

# User model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    study_hours = Column(Float, default=0)
    tasks_completed = Column(Integer, default=0)
    study_streak = Column(Integer, default=0)
    points = Column(Integer, default=0)
    desk_preferences = Column(JSON, default={})
    sound_volume = Column(Integer, default=50)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    study_rooms = relationship('StudyRoom', secondary=user_study_room, back_populates='users')

# StudyRoom model
class StudyRoom(Base):
    __tablename__ = 'study_rooms'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    users = relationship('User', secondary=user_study_room, back_populates='study_rooms')