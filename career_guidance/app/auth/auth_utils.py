import bcrypt
import re
from datetime import datetime
from app.database.crud import create_user, get_user_by_username
from app.database.session import get_db

def validate_email(email: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email))

def validate_phone(phone: str) -> bool:
    return bool(re.match(r"^\d{10}$", phone))

def register_user(user_data: dict) -> tuple:
    db = next(get_db())
    
    if not user_data.get('name'):
        return False, "Full name is required"
    if not validate_email(user_data.get('email', '')):
        return False, "Invalid email format"
    if not validate_phone(user_data.get('phone', '')):
        return False, "Phone must be 10 digits"
    if len(user_data.get('password', '')) < 8:
        return False, "Password must be at least 8 characters"
    if user_data['password'] != user_data['confirm_password']:
        return False, "Passwords don't match"
    
    if get_user_by_username(db, user_data['username']):
        return False, "Username already exists"
    
    hashed = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
    
    try:
        create_user(db, {
            'username': user_data['username'],
            'email': user_data['email'],
            'phone': user_data['phone'],
            'name': user_data['name'],
            'password_hash': hashed.decode('utf-8')
        })
        return True, "Registration successful!"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def verify_user(username: str, password: str) -> tuple:
    db = next(get_db())
    user = get_user_by_username(db, username)
    
    if not user:
        return False, None
    
    if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return True, user.id
    return False, None