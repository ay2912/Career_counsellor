from sqlalchemy import create_engine , inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from pathlib import Path
import os

# Database configuration
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DATA_DIR / 'career_guidance.db'}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True
)

# Create declarative base
Base = declarative_base()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database and create tables"""
    # IMPORT MODELS HERE AFTER Base IS CREATED
    from .models import User, Conversation, CareerSuggestion
    
    print(f"Creating database at: {DATABASE_URL}")
    print(f"Models to create: {Base.metadata.tables.keys()}")  # Debug print
    
    # This will create all tables
    Base.metadata.create_all(bind=engine)
    
    # Verify creation
    inspector = inspect(engine)
    print(f"Tables in database: {inspector.get_table_names()}")

def get_db():
    """Get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()