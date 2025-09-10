from sqlalchemy.orm import Session
from .models import User, Conversation, CareerSuggestion, Questionnaire
from typing import List, Optional, Dict

def create_user(db: Session, user_data: dict):
    db_user = User(
        username=user_data['username'],
        email=user_data['email'],
        phone=user_data['phone'],
        name=user_data['name'],
        password_hash=user_data['password_hash']
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def save_conversation(db: Session, user_id: int, session_id: str, role: str, content: str):
    db_conv = Conversation(
        user_id=user_id,
        session_id=session_id,
        role=role,
        content=content
    )
    db.add(db_conv)
    db.commit()
    return db_conv

def get_user_conversations(db: Session, user_id: int, session_id: Optional[str] = None) -> List[Conversation]:
    query = db.query(Conversation).filter(Conversation.user_id == user_id)
    if session_id:
        query = query.filter(Conversation.session_id == session_id)
    return query.order_by(Conversation.created_at).all()


def save_career_suggestions(db: Session, user_id: int, session_id: str, suggestions: List[dict]):
    saved = []
    for suggestion in suggestions:
        db_suggestion = CareerSuggestion(
            user_id=user_id,
            session_id=session_id,
            occupation=suggestion['occupation'],
            skills=suggestion['skills'],
            reasoning=suggestion.get('reasoning'),
            growth_potential=suggestion.get('growth_potential'),
            salary_range=suggestion.get('salary_range')
        )
        db.add(db_suggestion)
        saved.append(db_suggestion)
    db.commit()
    return saved

def get_user_career_suggestions(db: Session, user_id: int) -> List[CareerSuggestion]:
    return db.query(CareerSuggestion).filter(
        CareerSuggestion.user_id == user_id
    ).order_by(CareerSuggestion.created_at).all()

def get_suggestions_by_session(db: Session, session_id: str) -> List[CareerSuggestion]:
    return db.query(CareerSuggestion).filter(
        CareerSuggestion.session_id == session_id
    ).all()

def get_questionnaire_data(db: Session, user_id: int) -> Optional[Dict]:
    """Get user's questionnaire data if exists"""
    result = db.query(Questionnaire).filter(
        Questionnaire.user_id == user_id
    ).first()
    return result.__dict__ if result else None

def save_questionnaire(db: Session, user_id: int, data: Dict) -> Dict:
    """Save or update questionnaire data"""
    # Check if exists
    existing = db.query(Questionnaire).filter(
        Questionnaire.user_id == user_id
    ).first()
    
    if existing:
        # Update existing
        for key, value in data.items():
            setattr(existing, key, value)
    else:
        # Create new
        existing = Questionnaire(
            user_id=user_id,
            **data
        )
        db.add(existing)
    
    db.commit()
    db.refresh(existing)
    return existing.__dict__

def delete_conversation_history(db: Session, user_id: int) -> int:
    """Delete all conversation history for a user"""
    try:
        deleted_count = db.query(Conversation)\
                         .filter(Conversation.user_id == user_id)\
                         .delete()
        db.commit()
        return deleted_count
    except Exception as e:
        db.rollback()
        raise e