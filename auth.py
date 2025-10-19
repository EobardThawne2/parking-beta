"""Minimal auth module for the parking application.

Provides a tiny, safe in-memory + sqlite-backed wrapper that implements the
functions used by app.py so the project can run without ModuleNotFoundError.

Functions:
- init_auth_tables(): ensure auth tables exist (delegates to database module)
- authenticate_user(email, password): returns dict {success: bool, user: {...}}
- create_user(email, password, full_name, phone): creates and returns {success, user_id}
- get_user_by_id(user_id): returns user dict or None

This implementation is intentionally small and suitable for development/testing.
"""
from typing import Optional, Dict, Any
import hashlib
import database

# Simple password hashing for demo only (not for production)

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def init_auth_tables():
    """Create auth tables via the database module if available.
    Falls back to an in-memory structure if database doesn't provide expected
    functions.
    """
    try:
        if hasattr(database, 'init_auth_tables'):
            database.init_auth_tables()
            return
    except Exception:
        pass
    # database doesn't provide auth table initialization; nothing else to do.


def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    """Authenticate a user by email and password.

    Returns a dict matching the shape expected by app.py, e.g.
    { 'success': True, 'user': { 'id': ..., 'email': ..., 'full_name': ..., 'user_type': ... } }
    """
    if not email or not password:
        return {'success': False, 'message': 'Email and password are required'}
        
    hashed = _hash_password(password)
    
    try:
        user = database.get_user_by_email(email)
        if user and user.get('password_hash') == hashed:
            return {'success': True, 'user': user}
        return {'success': False, 'message': 'Invalid email or password'}
    except Exception as e:
        return {'success': False, 'message': f'Authentication error: {str(e)}'}


def create_user(email: str, password: str, full_name: str, phone: Optional[str] = None) -> Dict[str, Any]:
    """Create a user. Returns a dict: { success: bool, user_id: int }

    Delegates to database.create_user if available.
    """
    if not email or not password or not full_name:
        return {'success': False, 'message': 'Email, password, and full name are required'}
        
    hashed = _hash_password(password)
    
    try:
        user_id = database.create_user(email=email, password_hash=hashed, full_name=full_name, phone=phone)
        return {'success': True, 'user_id': user_id}
    except ValueError as e:
        return {'success': False, 'message': str(e)}
    except Exception as e:
        return {'success': False, 'message': f'User creation error: {str(e)}'}


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Return user dict or None. Delegates to database if possible."""
    try:
        return database.get_user_by_id(user_id)
    except Exception:
        return None
