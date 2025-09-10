from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from .session import Base  # IMPORT BASE FROM SESSION
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15))
    name = Column(String(100))
    password_hash = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(String(50), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CareerSuggestion(Base):
    __tablename__ = 'career_suggestions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(String(50), nullable=False)
    occupation = Column(Text, nullable=False)
    skills = Column(Text, nullable=False)
    reasoning = Column(Text)
    growth_potential = Column(String(50))
    salary_range = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class Questionnaire(Base):
    __tablename__ = 'questionnaires'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100))
    age = Column(Integer)
    personality = Column(Text)
    work_experience = Column(Text)
    resume_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)